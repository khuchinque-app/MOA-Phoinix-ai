**Intent Analysis & Track Selection**
The user is asking for a comprehensive `plan.md` file that outlines the full installation and architectural setup for their MoA (Mixture of Agents) swarm system. This includes integrating various tools (swarm-mcp, ztk, OpenTabs, etc.) and the "Heart Bleed" function discussed in the history. Since the user is requesting a technical implementation plan/architecture document to be used by a coding agent, this falls under **TRACK A: Code & Design Logic**.

---

**TRACK A: Code & Design Logic**

**Analysis & Planning**
1.  **Core Purpose:** To provide a master blueprint (`plan.md`) that a coding agent can follow to deploy a multi-agent swarm architecture on VPS infrastructure, utilizing MoA logic and a specific toolstack for browser/OS automation.
2.  **Common Mistakes/Anti-patterns:** 
    *   Sequential installation of dependencies that could be parallelized.
    *   Hard-coding API keys instead of using environment variables.
    *   Overlooking the Docker networking requirements for `swarm-mcp` to communicate with the host/other containers.
    *   Failing to implement a health-check mechanism for the VPS-distributed agents.
3.  **Standalone vs. System:** This is a system-level architecture. The "Heart Bleed" function is a core utility; `swarm-mcp` is the orchestrator; the browser tools are the "hands."
4.  **Internal/External Dependencies:**
    *   *External:* Docker, Python 3.10+, Node.js (for certain MCPs), GLM-4.7-flash/Claude/Gemini APIs, `browserbase` (SDK), `ztk` (binary).
    *   *Internal:* `heart_bleed.py` (Model call wrapper), `plan.md` (The blueprint).
5.  **Dependent Components:** The `SwarmRouter` (implied) and the final `Aggregator` model depend on the successful deployment of the Proposer agents and the `heart_bleed` utility.
6.  **Implementation Plan:**
    *   **Phase 1: Infrastructure.** VPS setup $\rightarrow$ Docker installation $\rightarrow$ `ztk` binary deployment.
    *   **Phase 2: Orchestration.** `swarm-mcp` installation $\rightarrow$ Docker image build for agent environments.
    *   **Phase 3: Tooling.** Install `browserbase` $\rightarrow$ Configure OpenTabs $\rightarrow$ Wire Chrome DevTools MCP.
    *   **Phase 4: Logic Layer.** Deploy `heart_bleed.py` $\rightarrow$ Configure MoA Proposer/Aggregator roles.
    *   **Phase 5: Validation.** End-to-end test: Proposer $\rightarrow$ Tool Use $\rightarrow$ Aggregator output.

**Architectural Briefing**

Since the Trunk model will synthesize the actual `.md` file, I am providing the structural requirements and critical snippets.

**Critical Components for the Plan:**
*   **Environment Variables:** Must specify a `.env` template containing `API_KEYS`, `VPS_IPs`, and `DOCKER_REGISTRY`.
*   **The "Heart Bleed" Integration:** The plan must specify that `heart_bleed.py` be placed in the base image used by `swarm-mcp` so all spawned agents have native model-calling capabilities.
*   **OpenTabs Logic:** Position it as the "API-first" layer, distinct from the "UI-first" Chrome DevTools MCP.

**File Structure Recommendation:**
```text
/moa-swarm-root
├── .env                  # Secrets and Config
├── plan.md               # The Master Blueprint
├── scripts/
│   ├── install_deps.sh   # Automation for VPS setup
│   └── setup_docker.sh   # swarm-mcp image config
├── core/
│   └── heart_bleed.py    # The model call function
└── agents/
    ├── proposer_config.json
    └── aggregator_config.json
```

**Recommendations for Trunk Model:**
1.  **Format:** Use a high-visibility Markdown format with checkboxes (`- [ ]`) for each installation step so the coding agent can "check off" progress.
2.  **Clarity:** Explicitly separate the "Standard Install" from the "MoA Configuration."
3.  **Tool Mapping:** Use a table to map the tool to its specific role (e.g., OpenTabs $\rightarrow$ API Browser, os-ai $\rightarrow$ OS Control).
4.  **Verification:** Include a "Smoke Test" section at the end of the plan to verify the swarm is alive.

**Handoff to Sunbird Trunk Model:**
The user wants the *complete* `plan.md`. Please synthesize the above analysis into a professional, technical blueprint. Ensure the "Heart Bleed" function is integrated as a foundational utility and that the toolstack (OpenTabs, ztk, swarm-mcp, browserbase) is organized by layer (Infrastructure $\rightarrow$ Orchestration $\rightarrow$ Perception $\rightarrow$ Action).
3DR Core Analysis
# # MoA Swarm Architecture Plan.md

## Components

### 1. OS-Level Control

| Component | Role | Description |
|-----------|------|-------------|
| os-ai-computer-use | Full desktop automation | Provides complete computer control, including screenshots, mouse movements, typing, and clicking. Requires significant setup but offers the most comprehensive control. |
| Windows-Use | Windows-specific automation | Similar to os-ai-computer-use but tailored for Windows VPS. Not useful for Linux-based VPS. |

### 2. Browser-Specific

| Component | Role | Description |
|-----------|------|-------------|
| bytebot | Browser automation | Optimized for browser automation, lighter than OS-level agents, and faster. Limited to browser window tasks. |
| browserbase | Browser session management | SDK for programmatic control over browser sessions, including stealth proxies and session management. Used as infrastructure under agents. |
| Chrome DevTools MCP | Browser control via DevTools Protocol | Exposes Chrome's DevTools Protocol for precise browser control, including element inspection, screenshots, and network request interception. |
| OpenTabs | API-first browser automation | API-focused browser automation framework designed for AI agents, providing a service integration layer. |

### 3. Niche Tier

| Component | Role | Description |
|-----------|------|-------------|
| open-codex-computer-use | Codex-optimized automation | Integrates well with coding workflows, bridging code generation and testing in a browser. Less general than os-ai-computer-use. |
| OpenPhone | Phone automation | Automation for mobile interfaces and phone apps. Useful for interacting with mobile applications. |
| anysearch mcp + vision mcp | Web perception | Sensory tools for web search and visual understanding, not full agents. Essential for agent perception. |

### 4. Infrastructure and Optimization

| Component | Role | Description |
|-----------|------|-------------|
| ztk | Token compression | CLI proxy that reduces LLM token consumption by compressing shell command output. Helps in optimizing token usage. |
| swarm-mcp | Agent orchestration | MCP server that allows spawning and managing multiple agents, enabling parallel processing and complex workflows. |

### 5. Heart Bleed Model Function

**Description:**
The Heart Bleed model function is designed for model calls within an MoA agent swarm architecture. It supports batch processing, error handling, and swarm-mcp compatibility.

**Key Features:**
- **Async Native:** Supports concurrent model calls for efficient processing.
- **Aggregator Built-in:** Synthesizes outputs from multiple agents.
- **Tracing Metadata:** Includes latency and token usage data for performance tracking.
- **Batch Support:** Enables parallel processing of multiple tasks.

**Code Structure:**
```python
"""
heart_bleed.py — Model call function for MoA agent swarm
Designed to integrate with swarm-mcp as a tool callable by any agent in the swarm.
"""

import json
import time
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

import aiohttp
import requests

# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
# Swap this to your model endpoint: glm-4.7-flash, Claude, Gemini, etc.

@dataclass
class HeartBleedConfig:
    """Per-call configuration — maps directly to your JSON payload structure."""
    model: str = "glm-4.7-flash"
    reasoning_effort: str = "none"  # none | low | medium | high
    max_tokens: int = 400
    temperature: float = 0.7
    api_url: str = DEFAULT_API_URL
    api_key: Optional[str] = None
    timeout: int = 30

# ─── Core Function ────────────────────────────────────────────────────────────

def heart_bleed_call(
    messages: List[Dict[str, str]],
    config: Optional[HeartBleedConfig] = None,
    **overrides
) -> Dict[str, Any]:
    """
    Single synchronous model call. Returns the full API response.

    Args:
        messages: [{"role": "user", "content": "..."}]
        config: HeartBleedConfig instance (optional)
        **overrides: Override any config field inline (model=, max_tokens=, etc.)

    Returns:
        API response dict with 'choices', 'usage', 'error' if failed.
    """
    if config is None:
        config = HeartBleedConfig()

    # Apply overrides
    for k, v in overrides.items():
        if hasattr(config, k):
            setattr(config, k, v)

    payload = {
        "model": config.model,
        "reasoning_effort": config.reasoning_effort,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "messages": messages
    }

    headers = {
        "Content-Type": "application/json",
    }
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    try:
        response = requests.post(
            config.api_url,
            headers=headers,
            json=payload,
            timeout=config.timeout
        )
        response.raise_for_status()
        result = response.json()
        # Add metadata for tracing
        result["_meta"] = {
            "model": config.model,
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "latency_ms": response.elapsed.total_seconds() * 1000
        }
        return result
    except requests.exceptions.Timeout:
        return {"error": f"Request timed out after {config.timeout}s", "_meta": {"model": config.model}}
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "_meta": {"model": config.model}}

# ─── Async Version (for concurrent calls in swarm-mcp) ────────────────────────

async def heart_bleed_call_async(
    messages: List[Dict[str, str]],
    config: Optional[HeartBleedConfig] = None,
    **overrides
) -> Dict[str, Any]:
    """Async version — use this when calling multiple models in parallel."""
    if config is None:
        config = HeartBleedConfig()

    for k, v in overrides.items():
        if hasattr(config, k):
            setattr(config, k, v)

    payload = {
        "model": config.model,
        "reasoning_effort": config.reasoning_effort,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "messages": messages
    }

    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            async with session.post(
                config.api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                result = await response.json()
                elapsed = (time.time() - start) * 1000
                result["_meta"] = {
                    "model": config.model,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "latency_ms": elapsed
                }
                return result
    except asyncio.TimeoutError:
        return {"error": f"Request timed out after {config.timeout}s", "_meta": {"model": config.model}}
    except Exception as e:
        return {"error": str(e), "_meta": {"model": config.model}}

# ─── MoA Batch Call ───────────────────────────────────────────────────────────

async def moa_batch_call(
    tasks: List[Dict[str, Any]],
    config: Optional[HeartBleedConfig] = None
) -> List[Dict[str, Any]]:
    """
    Fire multiple model calls in parallel — core of your MoA proposer pattern.

    Each task dict expects:
        "messages": [...]
        Optional overrides: "model", "max_tokens", "reasoning_effort", etc.

    Returns list of responses in the same order as tasks.
    """
    async def call_single(task):
        task_config = HeartBleedConfig() if config is None else config
        msgs = task.pop("messages")
        return await heart_bleed_call_async(msgs, task_config, **task)

    return await asyncio.gather(*[call_single(t) for t in tasks])

# ─── MoA Aggregator ──────────────────────────────────────────────────────────

def moa_aggregate(
    proposer_responses: List[Dict[str, Any]],
    aggregator_config: HeartBleedConfig
) -> Dict[str, Any]:
    """
    Takes N proposer outputs and asks an aggregator model to synthesize them.
    """
    # Build the aggregation prompt
    proposer_texts = []
    for i, resp in enumerate(proposer_responses):
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        proposer_texts.append(f"--- Proposer {i+1} ---\n{content}")

    aggregation_prompt = (
        "Below are responses from multiple AI agents analyzing the same input.\n"
        "Synthesize them into a single, coherent, refined response. "
        "Resolve contradictions, combine strengths, discard weaknesses.\n\n"
        + "\n\n".join(proposer_texts)
    )

    return heart_bleed_call(
        messages=[{"role": "user", "content": aggregation_prompt}],
        config=aggregator_config
    )

# ─── Usage Example ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Single call (matches your exact JSON)
    result = heart_bleed_call(
        messages=[{"role": "user", "content": "Summarize this diff in two lines: ..."}],
        model="glm-4.7-flash",
        reasoning_effort="none",
        max_tokens=400
    )
    print(json.dumps(result, indent=2))

    # Or run the async batch for MoA proposer phase:
    # asyncio.run(moa_batch_call([
    #     {"messages": [{"role": "user", "content": "Analyze from security angle"}], "model": "claude-3-opus"},
    #     {"messages": [{"role": "user", "content": "Analyze from performance angle"}], "model": "gpt-4"},
    #     {"messages": [{"role": "user", "content": "Analyze from UX angle"}], "model": "glm-4.7-flash"}
    # ]))
```

## Integration

### 1. Component Integration

**Description:**
Integrate the Heart Bleed model function into the swarm-mcp orchestration layer. This allows agents to call the function through the orchestration layer, enabling efficient and parallel processing.

**Steps:**
1. **Install swarm-mcp:** Set up the swarm-mcp server to manage and orchestrate agents.
2. **Integrate Heart Bleed Function:** Wire the Heart Bleed model function into swarm-mcp as an MCP tool definition.
3. **Configure Agents:** Set up agents to use the Heart Bleed function for model calls.
4. **Implement Batch Processing:** Use the `moa_batch_call` function for concurrent model calls.
5. **Synthesize Results:** Use the `moa_aggregate` function to synthesize outputs from multiple agents.

### 2. OpenTabs Integration

**Description:**
Integrate OpenTabs into the MoA swarm architecture for API-first browser automation.

**Steps:**
1. **Install OpenTabs:** Set up OpenTabs to provide API-focused browser automation.
2. **Configure Browser Sessions:** Use OpenTabs to manage browser sessions, including stealth proxies and session persistence.
3. **Integrate with Agents:** Allow agents to use OpenTabs for browser-related tasks, ensuring efficient and automated browser interactions.

### 3. ztk Integration

**Description:**
Integrate ztk to optimize token usage by compressing shell command output.

**Steps:**
1. **Install ztk:** Set up ztk as a CLI proxy to reduce LLM token consumption.
2. **Configure Token Compression:** Use ztk to compress shell command output before passing it to the LLM.
3. **Integrate with Agents:** Ensure agents use ztk for shell command processing to optimize token usage.

## Implementation Plan

### 1. Initial Setup

**Steps:**
1. **Install Dependencies:** Install all necessary dependencies, including swarm-mcp, OpenTabs, and ztk.
2. **Configure Environment:** Set up the environment for agent orchestration, including Docker containers and network policies.
3. **Initialize Agents:** Initialize agents with the necessary tools and configurations.

### 2. Agent Configuration

**Steps:**
1. **Configure OS-Level Agents:** Set up os-ai-computer-use or Windows-Use for full desktop automation.
2. **Configure Browser Agents:** Set up bytebot, browserbase, and Chrome DevTools MCP for browser-specific tasks.
3. **Configure Niche Agents:** Set up open-codex-computer-use and OpenPhone for specialized tasks.
4. **Integrate Heart Bleed Function:** Wire the Heart Bleed function into the agent configuration.

### 3. Workflow Implementation

**Steps:**
1. **Implement Proposer Phase:** Use `moa_batch_call` to fire multiple model calls in parallel.
2. **Implement Aggregator Phase:** Use `moa_aggregate` to synthesize outputs from multiple agents.
3. **Implement Error Handling:** Ensure robust error handling and retry mechanisms.
4. **Optimize Token Usage:** Integrate ztk to compress shell command output.

### 4. Testing and Validation

**Steps:**
1. **Test Components:** Test each component individually to ensure proper functioning.
2. **Test Integration:** Test the integration of components to ensure seamless operation.
3. **Validate Workflows:** Validate the entire workflow to ensure efficient and accurate processing.
4. **Optimize Performance:** Optimize the performance of the MoA swarm architecture.

## Conclusion

The MoA swarm architecture plan provides a comprehensive approach to integrating various components and tools for efficient and scalable agent orchestration. By following the outlined steps, you can build a robust and optimized MoA swarm architecture that leverages the strengths of each component.
