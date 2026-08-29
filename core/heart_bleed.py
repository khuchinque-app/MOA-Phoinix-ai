"""
heart_bleed.py — Model call function for MoA agent swarm

Designed to integrate with swarm-mcp as a tool callable by any agent in the swarm.
Supports synchronous and asynchronous calls, batch processing, and MoA aggregation.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import json
import time
import asyncio
import os
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "glm-4.7-flash"
DEFAULT_MAX_TOKENS = 400
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 30


# ─── Enums ─────────────────────────────────────────────────────────────────────

class ReasoningEffort(Enum):
    """Reasoning effort levels for model calls."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelProvider(Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GLM = "glm"
    CUSTOM = "custom"


# ─── Configuration ─────────────────────────────────────────────────────────────

@dataclass
class HeartBleedConfig:
    """
    Per-call configuration — maps directly to your JSON payload structure.
    
    This configuration controls all aspects of a model call, from the model
    selection to token limits and timeout settings.
    
    Attributes:
        model: The model identifier (e.g., "glm-4.7-flash", "claude-3-opus")
        reasoning_effort: Reasoning effort level (none, low, medium, high)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 2.0)
        api_url: API endpoint URL
        api_key: API authentication key
        timeout: Request timeout in seconds
        provider: Model provider (openai, anthropic, glm, custom)
    """
    
    model: str = DEFAULT_MODEL
    reasoning_effort: str = ReasoningEffort.NONE.value
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    api_url: str = DEFAULT_API_URL
    api_key: Optional[str] = None
    timeout: int = DEFAULT_TIMEOUT
    provider: ModelProvider = ModelProvider.CUSTOM
    
    def __post_init__(self):
        """Validate and normalize configuration after initialization."""
        # Auto-detect provider from API URL if not explicitly set
        if self.provider == ModelProvider.CUSTOM:
            if "openai.com" in self.api_url:
                self.provider = ModelProvider.OPENAI
            elif "anthropic.com" in self.api_url:
                self.provider = ModelProvider.ANTHROPIC
            elif "bigmodel.cn" in self.api_url:
                self.provider = ModelProvider.GLM
        
        # Auto-load API key from environment if not provided
        if self.api_key is None:
            self.api_key = self._load_api_key_from_env()
    
    def _load_api_key_from_env(self) -> Optional[str]:
        """Load API key from environment variables based on provider."""
        if self.provider == ModelProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == ModelProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == ModelProvider.GLM:
            return os.getenv("GLM_API_KEY")
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for API payload."""
        return {
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


# ─── Response Models ──────────────────────────────────────────────────────────

@dataclass
class ResponseMeta:
    """Metadata attached to every API response."""
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    provider: str = ""
    error: Optional[str] = None


@dataclass
class ModelResponse:
    """Structured response from a model call."""
    choices: List[Dict[str, Any]] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)
    _meta: Optional[ResponseMeta] = None
    error: Optional[str] = None
    
    @property
    def content(self) -> str:
        """Extract content from the first choice."""
        if self.choices and len(self.choices) > 0:
            return self.choices[0].get("message", {}).get("content", "")
        return ""
    
    @property
    def is_error(self) -> bool:
        """Check if this response represents an error."""
        return self.error is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "choices": self.choices,
            "usage": self.usage,
        }
        if self._meta:
            result["_meta"] = {
                "model": self._meta.model,
                "tokens_used": self._meta.tokens_used,
                "latency_ms": self._meta.latency_ms,
                "provider": self._meta.provider,
                "error": self._meta.error,
            }
        if self.error:
            result["error"] = self.error
        return result


# ─── Core Functions ────────────────────────────────────────────────────────────

def heart_bleed_call(
    messages: List[Dict[str, str]],
    config: Optional[HeartBleedConfig] = None,
    **overrides
) -> Dict[str, Any]:
    """
    Single synchronous model call. Returns the full API response.
    
    This is the foundational function for all model interactions in the MoA
    swarm. It handles authentication, payload construction, error handling,
    and response metadata.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
                  Example: [{"role": "user", "content": "Summarize this diff"}]
        config: HeartBleedConfig instance (optional, uses defaults if not provided)
        **overrides: Override any config field inline (model=, max_tokens=, etc.)
    
    Returns:
        API response dict with 'choices', 'usage', '_meta' metadata, or 'error'
    
    Example:
        >>> result = heart_bleed_call(
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     model="glm-4.7-flash",
        ...     max_tokens=100
        ... )
        >>> print(result["choices"][0]["message"]["content"])
    """
    if config is None:
        config = HeartBleedConfig()
    
    # Apply overrides to config
    for k, v in overrides.items():
        if hasattr(config, k):
            setattr(config, k, v)
    
    # Build payload
    payload = config.to_dict()
    payload["messages"] = messages
    
    # Build headers
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    
    # Execute request
    start_time = time.time()
    try:
        response = requests.post(
            config.api_url,
            headers=headers,
            json=payload,
            timeout=config.timeout
        )
        response.raise_for_status()
        result = response.json()
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract token usage
        usage = result.get("usage", {})
        tokens_used = usage.get("total_tokens", 0)
        
        # Attach metadata
        result["_meta"] = {
            "model": config.model,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "provider": config.provider.value,
        }
        
        return result
        
    except requests.exceptions.Timeout:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "error": f"Request timed out after {config.timeout}s",
            "_meta": {
                "model": config.model,
                "tokens_used": 0,
                "latency_ms": latency_ms,
                "provider": config.provider.value,
                "error": "timeout"
            }
        }
    except requests.exceptions.RequestException as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "error": str(e),
            "_meta": {
                "model": config.model,
                "tokens_used": 0,
                "latency_ms": latency_ms,
                "provider": config.provider.value,
                "error": str(e)
            }
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "error": f"Unexpected error: {str(e)}",
            "_meta": {
                "model": config.model,
                "tokens_used": 0,
                "latency_ms": latency_ms,
                "provider": config.provider.value,
                "error": str(e)
            }
        }


# ─── Async Version (for concurrent calls in swarm-mcp) ────────────────────────

async def heart_bleed_call_async(
    messages: List[Dict[str, str]],
    config: Optional[HeartBleedConfig] = None,
    **overrides
) -> Dict[str, Any]:
    """
    Async version — use this when calling multiple models in parallel.
    
    This function is critical for the MoA proposer phase, where multiple
    model calls must be fired concurrently to minimize total latency.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        config: HeartBleedConfig instance (optional)
        **overrides: Override any config field inline
    
    Returns:
        API response dict with 'choices', 'usage', '_meta' metadata, or 'error'
    """
    if config is None:
        config = HeartBleedConfig()
    
    # Apply overrides
    for k, v in overrides.items():
        if hasattr(config, k):
            setattr(config, k, v)
    
    # Build payload
    payload = config.to_dict()
    payload["messages"] = messages
    
    # Build headers
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    
    # Execute async request
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                result = await response.json()
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract token usage
                usage = result.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)
                
                # Attach metadata
                result["_meta"] = {
                    "model": config.model,
                    "tokens_used": tokens_used,
                    "latency_ms": latency_ms,
                    "provider": config.provider.value,
                }
                
                return result
                
    except asyncio.TimeoutError:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "error": f"Request timed out after {config.timeout}s",
            "_meta": {
                "model": config.model,
                "tokens_used": 0,
                "latency_ms": latency_ms,
                "provider": config.provider.value,
                "error": "timeout"
            }
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "error": f"Async request failed: {str(e)}",
            "_meta": {
                "model": config.model,
                "tokens_used": 0,
                "latency_ms": latency_ms,
                "provider": config.provider.value,
                "error": str(e)
            }
        }


# ─── MoA Batch Call ────────────────────────────────────────────────────────────

async def moa_batch_call(
    tasks: List[Dict[str, Any]],
    config: Optional[HeartBleedConfig] = None
) -> List[Dict[str, Any]]:
    """
    Fire multiple model calls in parallel — core of your MoA proposer pattern.
    
    This function executes N model calls concurrently using asyncio.gather,
    which is essential for the proposer phase of the MoA architecture.
    
    Args:
        tasks: List of task dicts, each containing:
               - "messages": List of message dicts (required)
               - Optional overrides: "model", "max_tokens", "reasoning_effort", etc.
        config: Base HeartBleedConfig (optional, used if not overridden per task)
    
    Returns:
        List of responses in the same order as input tasks
    
    Example:
        >>> tasks = [
        ...     {"messages": [{"role": "user", "content": "Security review"}], "model": "claude-3-opus"},
        ...     {"messages": [{"role": "user", "content": "Performance review"}], "model": "gpt-4"},
        ... ]
        >>> responses = await moa_batch_call(tasks)
    """
    async def call_single(task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with its configuration."""
        task_config = HeartBleedConfig() if config is None else config
        
        # Extract messages from task
        msgs = task.pop("messages", [])
        if not msgs:
            return {
                "error": "No messages provided in task",
                "_meta": {"model": "unknown", "tokens_used": 0, "latency_ms": 0}
            }
        
        # Apply task-specific overrides
        task_overrides = {k: v for k, v in task.items() if k != "messages"}
        
        return await heart_bleed_call_async(msgs, task_config, **task_overrides)
    
    # Execute all tasks concurrently
    return await asyncio.gather(*[call_single(task) for task in tasks])


# ─── MoA Aggregator ───────────────────────────────────────────────────────────

def moa_aggregate(
    proposer_responses: List[Dict[str, Any]],
    aggregator_config: HeartBleedConfig
) -> Dict[str, Any]:
    """
    Takes N proposer outputs and asks an aggregator model to synthesize them.
    
    This is the heart of the MoA pattern. The aggregator receives responses
    from multiple proposer models and synthesizes them into a single,
    coherent, refined response.
    
    Args:
        proposer_responses: List of responses from proposer models
        aggregator_config: Configuration for the aggregator model
    
    Returns:
        Aggregated response dict with synthesized content
    
    Example:
        >>> config = HeartBleedConfig(model="claude-3-opus", max_tokens=800)
        >>> result = moa_aggregate(proposer_responses, config)
        >>> print(result["choices"][0]["message"]["content"])
    """
    # Build aggregation prompt from proposer outputs
    proposer_texts = []
    for i, resp in enumerate(proposer_responses):
        # Extract content from response
        if "choices" in resp and len(resp["choices"]) > 0:
            content = resp["choices"][0].get("message", {}).get("content", "")
        elif "error" in resp:
            content = f"[Error: {resp['error']}]"
        else:
            content = "[No content]"
        
        proposer_texts.append(f"--- Proposer {i+1} ---\n{content}")
    
    # Construct aggregation prompt
    aggregation_prompt = (
        "Below are responses from multiple AI agents analyzing the same input.\n"
        "Synthesize them into a single, coherent, refined response. "
        "Resolve contradictions, combine strengths, discard weaknesses.\n\n"
        + "\n\n".join(proposer_texts)
    )
    
    # Call aggregator model
    return heart_bleed_call(
        messages=[{"role": "user", "content": aggregation_prompt}],
        config=aggregator_config
    )


# ─── MoA Pipeline ─────────────────────────────────────────────────────────────

async def moa_pipeline(
    input_message: str,
    proposer_configs: List[HeartBleedConfig],
    aggregator_config: HeartBleedConfig,
    proposer_prompts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Complete MoA pipeline: Proposer Phase → Aggregation Phase.
    
    This is a high-level function that executes the full MoA workflow:
    1. Send input to multiple proposer models in parallel
    2. Collect proposer responses
    3. Aggregate responses into a final output
    
    Args:
        input_message: The input text to analyze
        proposer_configs: List of HeartBleedConfig for each proposer
        aggregator_config: Configuration for the aggregator model
        proposer_prompts: Optional custom prompts for each proposer
    
    Returns:
        Final aggregated response dict
    
    Example:
        >>> proposer_configs = [
        ...     HeartBleedConfig(model="claude-3-opus"),
        ...     HeartBleedConfig(model="gpt-4"),
        ...     HeartBleedConfig(model="glm-4.7-flash"),
        ... ]
        >>> aggregator_config = HeartBleedConfig(model="claude-3-opus", max_tokens=800)
        >>> result = await moa_pipeline("Review this code", proposer_configs, aggregator_config)
    """
    # Step 1: Build proposer tasks
    proposer_tasks = []
    for i, config in enumerate(proposer_configs):
        # Use custom prompt if provided, otherwise use default
        if proposer_prompts and i < len(proposer_prompts):
            prompt = proposer_prompts[i]
        else:
            prompt = f"Analyze the following input:\n\n{input_message}"
        
        proposer_tasks.append({
            "messages": [{"role": "user", "content": prompt}],
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "reasoning_effort": config.reasoning_effort,
        })
    
    # Step 2: Execute proposer phase (parallel)
    proposer_responses = await moa_batch_call(proposer_tasks)
    
    # Step 3: Execute aggregation phase
    final_response = moa_aggregate(proposer_responses, aggregator_config)
    
    # Add pipeline metadata
    final_response["_pipeline"] = {
        "input_length": len(input_message),
        "proposer_count": len(proposer_configs),
        "proposer_models": [c.model for c in proposer_configs],
        "aggregator_model": aggregator_config.model,
        "proposer_latencies": [
            r.get("_meta", {}).get("latency_ms", 0) 
            for r in proposer_responses
        ],
    }
    
    return final_response


# ─── Utility Functions ─────────────────────────────────────────────────────────

def create_config_from_env() -> HeartBleedConfig:
    """
    Create a HeartBleedConfig from environment variables.
    
    Returns:
        HeartBleedConfig with values loaded from .env file
    """
    return HeartBleedConfig(
        model=os.getenv("DEFAULT_MODEL", DEFAULT_MODEL),
        api_url=os.getenv("DEFAULT_MODEL_ENDPOINT", DEFAULT_API_URL),
        max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))),
        temperature=float(os.getenv("DEFAULT_TEMPERATURE", str(DEFAULT_TEMPERATURE))),
        timeout=int(os.getenv("DEFAULT_TIMEOUT", str(DEFAULT_TIMEOUT))),
    )


def format_response(response: Dict[str, Any], pretty: bool = True) -> str:
    """
    Format a response dict for display.
    
    Args:
        response: Response dict from heart_bleed_call
        pretty: If True, format with indentation
    
    Returns:
        Formatted string
    """
    if pretty:
        return json.dumps(response, indent=2, ensure_ascii=False)
    return json.dumps(response, ensure_ascii=False)


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example 1: Single synchronous call (matches your exact JSON)
    print("=" * 60)
    print("Example 1: Single Synchronous Call")
    print("=" * 60)
    
    result = heart_bleed_call(
        messages=[{"role": "user", "content": "Summarize this diff in two lines: ..."}],
        model="glm-4.7-flash",
        reasoning_effort="none",
        max_tokens=400
    )
    print(format_response(result))
    
    # Example 2: MoA batch call (proposer phase)
    print("\n" + "=" * 60)
    print("Example 2: MoA Batch Call (Proposer Phase)")
    print("=" * 60)
    
    async def run_batch_example():
        tasks = [
            {"messages": [{"role": "user", "content": "Analyze from security angle"}], "model": "claude-3-opus"},
            {"messages": [{"role": "user", "content": "Analyze from performance angle"}], "model": "gpt-4"},
            {"messages": [{"role": "user", "content": "Analyze from UX angle"}], "model": "glm-4.7-flash"},
        ]
        responses = await moa_batch_call(tasks)
        for i, resp in enumerate(responses):
            print(f"\n--- Proposer {i+1} ---")
            print(format_response(resp))
    
    asyncio.run(run_batch_example())
    
    # Example 3: MoA aggregation
    print("\n" + "=" * 60)
    print("Example 3: MoA Aggregation")
    print("=" * 60)
    
    # Simulated proposer responses
    simulated_responses = [
        {"choices": [{"message": {"content": "Security analysis: No critical vulnerabilities found."}}]},
        {"choices": [{"message": {"content": "Performance analysis: Code is efficient but could optimize loops."}}]},
        {"choices": [{"message": {"content": "UX analysis: Good readability, but needs more comments."}}]},
    ]
    
    aggregator_config = HeartBleedConfig(
        model="claude-3-opus",
        max_tokens=800,
        temperature=0.3
    )
    
    aggregated = moa_aggregate(simulated_responses, aggregator_config)
    print(format_response(aggregated))
