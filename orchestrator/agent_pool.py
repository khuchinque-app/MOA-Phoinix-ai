"""
agent_pool.py — Agent pool management for MoA Swarm

Manages the lifecycle of agents, including creation, monitoring,
and resource allocation.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict

from core.config import get_config, MoASwarmConfig
from core.models import (
    AgentRole,
    AgentStatus,
    AgentConfig,
    Task,
    TaskStatus,
)


# ─── Agent ─────────────────────────────────────────────────────────────────────

class Agent:
    """
    Represents a single agent in the swarm.
    
    An agent has a specific role (proposer, aggregator, browser, etc.)
    and can execute tasks assigned to it.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize an agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.status = AgentStatus(
            agent_id=config.id,
            role=config.role,
            status=TaskStatus.PENDING,
        )
        self.created_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
    
    @property
    def id(self) -> str:
        """Get agent ID."""
        return self.config.id
    
    @property
    def role(self) -> AgentRole:
        """Get agent role."""
        return self.config.role
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available for tasks."""
        return self.status.status == TaskStatus.PENDING
    
    def update_heartbeat(self) -> None:
        """Update agent heartbeat timestamp."""
        self.last_heartbeat = datetime.utcnow()
    
    def start_task(self, task_id: str) -> None:
        """Mark agent as running a task."""
        self.status.status = TaskStatus.RUNNING
        self.status.current_task = task_id
    
    def complete_task(self, success: bool = True) -> None:
        """Mark agent as completing a task."""
        self.status.status = TaskStatus.PENDING
        self.status.current_task = None
        
        if success:
            self.status.tasks_completed += 1
        else:
            self.status.tasks_failed += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "role": self.role.value,
            "status": self.status.status.value,
            "current_task": self.status.current_task,
            "tasks_completed": self.status.tasks_completed,
            "tasks_failed": self.status.tasks_failed,
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
        }


# ─── Agent Pool ───────────────────────────────────────────────────────────────

class AgentPool:
    """
    Manages a pool of agents for the swarm.
    
    The agent pool handles:
    1. Agent creation and configuration
    2. Agent lifecycle management
    3. Task assignment and load balancing
    4. Health monitoring
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Agent Pool.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.agents: Dict[str, Agent] = {}
        self.task_history: List[Dict[str, Any]] = []
        
        # Statistics
        self._stats = {
            "total_agents_created": 0,
            "total_tasks_assigned": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
        }
    
    # ─── Agent Management ─────────────────────────────────────────────────────
    
    def create_agent(
        self,
        role: AgentRole,
        model: str = "glm-4.7-flash",
        max_tokens: int = 400,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            role: Agent role
            model: Model identifier
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            system_prompt: Optional system prompt
            **kwargs: Additional configuration
        
        Returns:
            Created Agent instance
        """
        agent_id = f"agent-{role.value}-{uuid.uuid4().hex[:8]}"
        
        config = AgentConfig(
            id=agent_id,
            role=role,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
            metadata=kwargs,
        )
        
        agent = Agent(config)
        self.agents[agent_id] = agent
        self._stats["total_agents_created"] += 1
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the pool."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with a specific role."""
        return [agent for agent in self.agents.values() if agent.role == role]
    
    def get_available_agents(self) -> List[Agent]:
        """Get all available agents."""
        return [agent for agent in self.agents.values() if agent.is_available]
    
    # ─── Task Assignment ──────────────────────────────────────────────────────
    
    def assign_task(self, task: Task) -> Optional[Agent]:
        """
        Assign a task to an available agent.
        
        Args:
            task: Task to assign
        
        Returns:
            Assigned Agent or None if no agent available
        """
        # Find available agents with matching role
        available_agents = [
            agent for agent in self.get_available_agents()
            if agent.role == task.role or task.role == AgentRole.PROPOSER
        ]
        
        if not available_agents:
            return None
        
        # Simple load balancing: select agent with fewest tasks
        agent = min(available_agents, key=lambda a: a.status.tasks_completed)
        
        # Assign task
        agent.start_task(task.id)
        self._stats["total_tasks_assigned"] += 1
        
        return agent
    
    def complete_task_assignment(self, agent_id: str, success: bool = True) -> None:
        """Mark a task assignment as complete."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.complete_task(success)
            
            if success:
                self._stats["total_tasks_completed"] += 1
            else:
                self._stats["total_tasks_failed"] += 1
    
    # ─── Pool Initialization ──────────────────────────────────────────────────
    
    def initialize_default_pool(self) -> Dict[AgentRole, List[Agent]]:
        """
        Initialize a default pool of agents based on configuration.
        
        Returns:
            Dictionary mapping roles to created agents
        """
        pool_size = self.config.swarm.agent_pool_size
        created_agents = defaultdict(list)
        
        # Create proposer agents
        proposer_count = max(2, pool_size // 2)
        for _ in range(proposer_count):
            agent = self.create_agent(
                role=AgentRole.PROPOSER,
                model="glm-4.7-flash",
            )
            created_agents[AgentRole.PROPOSER].append(agent)
        
        # Create aggregator agent
        aggregator = self.create_agent(
            role=AgentRole.AGGREGATOR,
            model="claude-3-opus",
            max_tokens=800,
            temperature=0.3,
        )
        created_agents[AgentRole.AGGREGATOR].append(aggregator)
        
        # Create browser agent
        browser = self.create_agent(
            role=AgentRole.BROWSER,
            model="glm-4.7-flash",
        )
        created_agents[AgentRole.BROWSER].append(browser)
        
        # Create search agent
        search = self.create_agent(
            role=AgentRole.SEARCH,
            model="glm-4.7-flash",
        )
        created_agents[AgentRole.SEARCH].append(search)
        
        return dict(created_agents)
    
    # ─── Health Monitoring ────────────────────────────────────────────────────
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check health of all agents in the pool.
        
        Returns:
            Health status dictionary
        """
        healthy = 0
        unhealthy = 0
        
        for agent in self.agents.values():
            # Check if agent heartbeat is recent (within 60 seconds)
            heartbeat_age = (datetime.utcnow() - agent.last_heartbeat).total_seconds()
            if heartbeat_age < 60:
                healthy += 1
            else:
                unhealthy += 1
        
        return {
            "total_agents": len(self.agents),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "available": len(self.get_available_agents()),
            "stats": self._stats.copy(),
        }
    
    def update_heartbeats(self) -> None:
        """Update heartbeats for all agents."""
        for agent in self.agents.values():
            agent.update_heartbeat()
    
    # ─── Statistics ───────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        role_counts = defaultdict(int)
        for agent in self.agents.values():
            role_counts[agent.role.value] += 1
        
        return {
            "total_agents": len(self.agents),
            "agents_by_role": dict(role_counts),
            "available_agents": len(self.get_available_agents()),
            "stats": self._stats.copy(),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pool to dictionary."""
        return {
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()},
            "stats": self.get_stats(),
        }


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize agent pool
    pool = AgentPool()
    
    # Initialize default pool
    print("Initializing default agent pool...")
    created_agents = pool.initialize_default_pool()
    
    for role, agents in created_agents.items():
        print(f"  Created {len(agents)} {role.value} agent(s)")
    
    # Check health
    print("\nAgent Pool Health:")
    health = pool.check_health()
    print(f"  Total agents: {health['total_agents']}")
    print(f"  Healthy: {health['healthy']}")
    print(f"  Available: {health['available']}")
    
    # Get stats
    print("\nPool Statistics:")
    stats = pool.get_stats()
    print(f"  Agents by role: {stats['agents_by_role']}")
    print(f"  Total tasks assigned: {stats['stats']['total_tasks_assigned']}")
