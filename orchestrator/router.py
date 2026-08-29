"""
router.py — Task routing and orchestration for MoA Swarm

Manages task distribution, agent selection, and workflow execution.
Routes tasks to appropriate agents based on type and requirements.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import uuid
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from enum import Enum

from core.heart_bleed import (
    heart_bleed_call,
    heart_bleed_call_async,
    moa_batch_call,
    moa_aggregate,
    HeartBleedConfig,
)
from core.config import get_config, MoASwarmConfig
from core.models import (
    Task,
    TaskStatus,
    AgentRole,
    ModelCallRequest,
    ModelCallResponse,
    BatchCallResponse,
    AggregationResponse,
    ResponseMetadata,
)


# ─── Routing Strategy ─────────────────────────────────────────────────────────

class RoutingStrategy(Enum):
    """Task routing strategies."""
    DIRECT = "direct"           # Single model call
    PARALLEL = "parallel"       # MoA proposer phase (parallel calls)
    SEQUENTIAL = "sequential"   # Sequential pipeline
    MOA = "moa"                 # Full MoA pipeline (parallel + aggregation)


# ─── Router ────────────────────────────────────────────────────────────────────

class SwarmRouter:
    """
    Routes tasks to appropriate agents and manages workflow execution.
    
    The router is the central orchestrator that:
    1. Receives tasks from users or other systems
    2. Determines the appropriate routing strategy
    3. Dispatches tasks to agents
    4. Collects and aggregates results
    5. Returns final outputs
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Swarm Router.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, Any] = {}
        
        # Task queue for sequential processing
        self._task_queue: asyncio.Queue = asyncio.Queue()
        
        # Callbacks for task events
        self._on_task_complete: Optional[Callable] = None
        self._on_task_failed: Optional[Callable] = None
    
    def set_callbacks(
        self,
        on_complete: Optional[Callable] = None,
        on_failed: Optional[Callable] = None
    ) -> None:
        """Set callback functions for task events."""
        self._on_task_complete = on_complete
        self._on_task_failed = on_failed
    
    # ─── Task Management ──────────────────────────────────────────────────────
    
    def create_task(
        self,
        input_text: str,
        role: AgentRole = AgentRole.PROPOSER,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Create a new task.
        
        Args:
            input_text: The input text for the task
            role: Agent role to handle the task
            metadata: Additional metadata
        
        Returns:
            Created Task instance
        """
        task = Task(
            id=str(uuid.uuid4()),
            input=input_text,
            role=role,
            metadata=metadata or {},
        )
        self.tasks[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Any = None, error: str = None) -> None:
        """Update task status."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            task.updated_at = datetime.utcnow()
            if result:
                task.result = result
            if error:
                task.error = error
    
    # ─── Routing Strategies ───────────────────────────────────────────────────
    
    async def route_direct(
        self,
        messages: List[Dict[str, str]],
        model: str = "glm-4.7-flash",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route a task to a single model (Direct strategy).
        
        Args:
            messages: List of message dicts
            model: Model identifier
            **kwargs: Additional model parameters
        
        Returns:
            Model response dict
        """
        config = HeartBleedConfig(model=model, **kwargs)
        return await heart_bleed_call_async(messages, config)
    
    async def route_parallel(
        self,
        tasks: List[Dict[str, Any]],
        base_config: Optional[HeartBleedConfig] = None
    ) -> List[Dict[str, Any]]:
        """
        Route tasks in parallel (MoA proposer phase).
        
        Args:
            tasks: List of task dicts with messages and overrides
            base_config: Base configuration for all tasks
        
        Returns:
            List of response dicts
        """
        return await moa_batch_call(tasks, base_config)
    
    def route_sequential(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Route tasks sequentially (pipeline strategy).
        
        Args:
            steps: List of step configs with messages and model
        
        Returns:
            List of response dicts
        """
        results = []
        for step in steps:
            messages = step.get("messages", [])
            model = step.get("model", "glm-4.7-flash")
            config = HeartBleedConfig(model=model)
            result = heart_bleed_call(messages, config)
            results.append(result)
        return results
    
    async def route_moa(
        self,
        input_message: str,
        proposer_configs: List[HeartBleedConfig],
        aggregator_config: HeartBleedConfig,
        proposer_prompts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Route a task through the full MoA pipeline.
        
        Args:
            input_message: The input text to analyze
            proposer_configs: List of configs for proposer models
            aggregator_config: Config for aggregator model
            proposer_prompts: Optional custom prompts for each proposer
        
        Returns:
            Aggregated response dict
        """
        # Build proposer tasks
        proposer_tasks = []
        for i, config in enumerate(proposer_configs):
            prompt = proposer_prompts[i] if proposer_prompts and i < len(proposer_prompts) else f"Analyze the following input:\n\n{input_message}"
            
            proposer_tasks.append({
                "messages": [{"role": "user", "content": prompt}],
                "model": config.model,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "reasoning_effort": config.reasoning_effort,
            })
        
        # Execute proposer phase
        proposer_responses = await moa_batch_call(proposer_tasks)
        
        # Execute aggregation phase
        final_response = moa_aggregate(proposer_responses, aggregator_config)
        
        # Add pipeline metadata
        final_response["_pipeline"] = {
            "input_length": len(input_message),
            "proposer_count": len(proposer_configs),
            "proposer_models": [c.model for c in proposer_configs],
            "aggregator_model": aggregator_config.model,
        }
        
        return final_response
    
    # ─── Task Execution ───────────────────────────────────────────────────────
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a task using the appropriate routing strategy.
        
        Args:
            task: Task to execute
        
        Returns:
            Task result dict
        """
        self.update_task_status(task.id, TaskStatus.RUNNING)
        
        try:
            # Determine routing strategy based on task role
            if task.role == AgentRole.PROPOSER:
                result = await self.route_direct(
                    messages=[{"role": "user", "content": task.input}],
                    model=task.metadata.get("model", "glm-4.7-flash"),
                )
            elif task.role == AgentRole.AGGREGATOR:
                # Aggregator needs proposer responses
                proposer_responses = task.metadata.get("proposer_responses", [])
                config = HeartBleedConfig(
                    model=task.metadata.get("model", "claude-3-opus"),
                    max_tokens=task.metadata.get("max_tokens", 800),
                )
                result = moa_aggregate(proposer_responses, config)
            else:
                # Default to direct routing
                result = await self.route_direct(
                    messages=[{"role": "user", "content": task.input}],
                )
            
            self.update_task_status(task.id, TaskStatus.COMPLETED, result=result)
            
            if self._on_task_complete:
                self._on_task_complete(task, result)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.update_task_status(task.id, TaskStatus.FAILED, error=error_msg)
            
            if self._on_task_failed:
                self._on_task_failed(task, error_msg)
            
            return {"error": error_msg}
    
    async def execute_batch(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: List of tasks to execute
        
        Returns:
            List of task results
        """
        return await asyncio.gather(*[self.execute_task(task) for task in tasks])
    
    # ─── Convenience Methods ──────────────────────────────────────────────────
    
    async def simple_call(
        self,
        prompt: str,
        model: str = "glm-4.7-flash",
        **kwargs
    ) -> str:
        """
        Simple convenience method for a single model call.
        
        Args:
            prompt: User prompt
            model: Model identifier
            **kwargs: Additional parameters
        
        Returns:
            Model response content string
        """
        result = await self.route_direct(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            **kwargs,
        )
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    async def moa_call(
        self,
        prompt: str,
        proposer_models: Optional[List[str]] = None,
        aggregator_model: str = "claude-3-opus",
        proposer_prompts: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Convenience method for a full MoA call.
        
        Args:
            prompt: User prompt
            proposer_models: List of proposer model identifiers
            aggregator_model: Aggregator model identifier
            proposer_prompts: Optional custom prompts for each proposer
            **kwargs: Additional parameters
        
        Returns:
            Aggregated response content string
        """
        if proposer_models is None:
            proposer_models = ["glm-4.7-flash", "claude-3-opus", "gpt-4"]
        
        proposer_configs = [
            HeartBleedConfig(model=m, **kwargs) for m in proposer_models
        ]
        aggregator_config = HeartBleedConfig(model=aggregator_model)
        
        result = await self.route_moa(
            input_message=prompt,
            proposer_configs=proposer_configs,
            aggregator_config=aggregator_config,
            proposer_prompts=proposer_prompts,
        )
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def main():
        # Initialize router
        router = SwarmRouter()
        
        # Example 1: Simple direct call
        print("=" * 60)
        print("Example 1: Simple Direct Call")
        print("=" * 60)
        
        result = await router.simple_call(
            "What is the capital of France?",
            model="glm-4.7-flash"
        )
        print(f"Response: {result}")
        
        # Example 2: MoA call
        print("\n" + "=" * 60)
        print("Example 2: MoA Call")
        print("=" * 60)
        
        result = await router.moa_call(
            "Review this code for security issues",
            proposer_models=["glm-4.7-flash"],
            aggregator_model="glm-4.7-flash",
        )
        print(f"Response: {result}")
        
        # Example 3: Task execution
        print("\n" + "=" * 60)
        print("Example 3: Task Execution")
        print("=" * 60)
        
        task = router.create_task(
            input_text="Analyze the performance of this function",
            role=AgentRole.PROPOSER,
            metadata={"model": "glm-4.7-flash"}
        )
        
        result = await router.execute_task(task)
        print(f"Task Status: {task.status}")
        print(f"Result: {result}")
    
    asyncio.run(main())
