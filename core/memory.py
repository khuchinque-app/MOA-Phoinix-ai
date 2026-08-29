"""
memory.py — Graph-Engineering Memory System for MoA Swarm

Implements knowledge graph memory architecture based on graph-engineering
principles from codejunkie99/graph-engineering.

Memory Types:
- Knowledge Graph: What agents remember (entities, relations, events)
- Task Graph: How agents work (jobs, dependencies, execution flow)
- Session Memory: Current context and state
- Collective Memory: Shared across agents

Architecture:
- Nodes: Entities, facts, tasks, agents
- Edges: Relationships with time and provenance
- Provenance: Every fact has source, timestamp, confidence

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import json
import uuid
import asyncio
from typing import Optional, Dict, Any, List, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
import hashlib


# ─── Node Types ──────────────────────────────────────────────────────────────

class NodeType:
    """Node types in the knowledge graph."""
    # Knowledge Graph nodes
    ENTITY = "entity"
    FACT = "fact"
    EVENT = "event"
    CONCEPT = "concept"
    
    # Task Graph nodes
    TASK = "task"
    JOB = "job"
    STEP = "step"
    
    # Agent nodes
    AGENT = "agent"
    MODEL = "model"
    
    # Memory nodes
    MEMORY = "memory"
    CONTEXT = "context"
    SESSION = "session"


# ─── Edge Types ──────────────────────────────────────────────────────────────

class EdgeType:
    """Edge types in the knowledge graph."""
    # Knowledge relations
    RELATED_TO = "RELATED_TO"
    DEPENDS_ON = "DEPENDS_ON"
    CAUSED_BY = "CAUSED_BY"
    PART_OF = "PART_OF"
    CREATED_BY = "CREATED_BY"
    USED_BY = "USED_BY"
    
    # Task relations
    EXECUTES = "EXECUTES"
    PRECEDES = "PRECEDES"
    PARALLEL_WITH = "PARALLEL_WITH"
    VERIFIES = "VERIFIES"
    
    # Memory relations
    REMEMBERS = "REMEMBERS"
    CONTEXT_OF = "CONTEXT_OF"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"


# ─── Provenance ──────────────────────────────────────────────────────────────

@dataclass
class Provenance:
    """Provenance metadata for every fact/node."""
    source: str
    extracted_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0
    agent_id: Optional[str] = None
    model: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "extracted_at": self.extracted_at.isoformat(),
            "confidence": self.confidence,
            "agent_id": self.agent_id,
            "model": self.model,
        }


# ─── Node ────────────────────────────────────────────────────────────────────

@dataclass
class Node:
    """A node in the knowledge/task graph."""
    id: str
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    provenance: Provenance = field(default_factory=lambda: Provenance(source="system"))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "properties": self.properties,
            "provenance": self.provenance.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ─── Edge ────────────────────────────────────────────────────────────────────

@dataclass
class Edge:
    """An edge in the knowledge/task graph."""
    id: str
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    provenance: Provenance = field(default_factory=lambda: Provenance(source="system"))
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "properties": self.properties,
            "provenance": self.provenance.to_dict(),
            "weight": self.weight,
            "created_at": self.created_at.isoformat(),
        }


# ─── Knowledge Graph ─────────────────────────────────────────────────────────

class KnowledgeGraph:
    """
    Knowledge graph for agent memory.
    
    Based on graph-engineering principles:
    - Schema first: Define ontology before extraction
    - Provenance on every fact: source, timestamp, confidence
    - Fusion before storage: Merge duplicates
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)  # node_id -> edge_ids
        self.type_index: Dict[str, Set[str]] = defaultdict(set)  # type -> node_ids
        self.name_index: Dict[str, str] = {}  # name -> node_id
        
    def add_node(
        self,
        type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
        provenance: Optional[Provenance] = None
    ) -> Node:
        """Add a node to the knowledge graph."""
        node_id = f"{type}:{name}:{uuid.uuid4().hex[:8]}"
        
        node = Node(
            id=node_id,
            type=type,
            name=name,
            properties=properties or {},
            provenance=provenance or Provenance(source="knowledge_graph"),
        )
        
        self.nodes[node_id] = node
        self.type_index[type].add(node_id)
        self.name_index[name] = node_id
        
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        type: str,
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
        provenance: Optional[Provenance] = None
    ) -> Optional[Edge]:
        """Add an edge between two nodes."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        edge_id = f"{source_id}->{target_id}:{type}"
        
        edge = Edge(
            id=edge_id,
            source_id=source_id,
            target_id=target_id,
            type=type,
            properties=properties or {},
            weight=weight,
            provenance=provenance or Provenance(source="knowledge_graph"),
        )
        
        self.edges[edge_id] = edge
        self.adjacency[source_id].add(edge_id)
        self.adjacency[target_id].add(edge_id)
        
        return edge
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_nodes_by_type(self, type: str) -> List[Node]:
        """Get all nodes of a specific type."""
        node_ids = self.type_index.get(type, set())
        return [self.nodes[nid] for nid in node_ids if nid in self.nodes]
    
    def get_node_by_name(self, name: str) -> Optional[Node]:
        """Get a node by name."""
        node_id = self.name_index.get(name)
        if node_id:
            return self.nodes.get(node_id)
        return None
    
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[Tuple[Node, Edge]]:
        """Get neighbors of a node with their connecting edges."""
        neighbors = []
        
        for edge_id in self.adjacency.get(node_id, set()):
            edge = self.edges.get(edge_id)
            if not edge:
                continue
            
            if edge_type and edge.type != edge_type:
                continue
            
            # Get the other node
            other_id = edge.target_id if edge.source_id == node_id else edge.source_id
            other_node = self.nodes.get(other_id)
            
            if other_node:
                neighbors.append((other_node, edge))
        
        return neighbors
    
    def query(
        self,
        node_type: Optional[str] = None,
        edge_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """Query the knowledge graph."""
        results = {
            "nodes": [],
            "edges": [],
            "paths": [],
        }
        
        # Filter nodes by type
        if node_type:
            nodes = self.get_nodes_by_type(node_type)
        else:
            nodes = list(self.nodes.values())
        
        # Filter by properties
        if properties:
            nodes = [
                n for n in nodes
                if all(n.properties.get(k) == v for k, v in properties.items())
            ]
        
        results["nodes"] = [n.to_dict() for n in nodes]
        
        # Get edges for these nodes
        for node in nodes:
            for edge_id in self.adjacency.get(node.id, set()):
                edge = self.edges.get(edge_id)
                if edge:
                    if edge_type and edge.type != edge_type:
                        continue
                    results["edges"].append(edge.to_dict())
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Export the entire graph as a dictionary."""
        return {
            "name": self.name,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": {eid: e.to_dict() for eid, e in self.edges.items()},
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": {t: len(ids) for t, ids in self.type_index.items()},
            },
        }
    
    def save(self, path: str) -> None:
        """Save the graph to a JSON file."""
        data = self.to_dict()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str) -> None:
        """Load the graph from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        
        self.name = data.get("name", self.name)
        
        # Load nodes
        for nid, n_data in data.get("nodes", {}).items():
            node = Node(
                id=n_data["id"],
                type=n_data["type"],
                name=n_data["name"],
                properties=n_data.get("properties", {}),
                provenance=Provenance(
                    source=n_data["provenance"]["source"],
                    confidence=n_data["provenance"].get("confidence", 1.0),
                ),
            )
            self.nodes[nid] = node
            self.type_index[node.type].add(nid)
            self.name_index[node.name] = nid
        
        # Load edges
        for eid, e_data in data.get("edges", {}).items():
            edge = Edge(
                id=e_data["id"],
                source_id=e_data["source_id"],
                target_id=e_data["target_id"],
                type=e_data["type"],
                properties=e_data.get("properties", {}),
                weight=e_data.get("weight", 1.0),
            )
            self.edges[eid] = edge
            self.adjacency[edge.source_id].add(eid)
            self.adjacency[edge.target_id].add(eid)


# ─── Task Graph ──────────────────────────────────────────────────────────────

class TaskGraph:
    """
    Task graph for agent orchestration.
    
    Based on graph-engineering task-graph patterns:
    - Diamond pattern: split → parallel workers → separate verifiers → merge
    - Stop rule: Teams win ~80% on work that splits
    - Human gate: Approval where mistakes are expensive
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.tasks: Dict[str, Node] = {}
        self.dependencies: Dict[str, Edge] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        
    def add_task(
        self,
        name: str,
        task_type: str = "job",
        properties: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Node:
        """Add a task to the graph."""
        task_id = f"task:{name}:{uuid.uuid4().hex[:8]}"
        
        node = Node(
            id=task_id,
            type=task_type,
            name=name,
            properties=properties or {},
            provenance=Provenance(source="task_graph", agent_id=agent_id),
        )
        
        self.tasks[task_id] = node
        return node
    
    def add_dependency(
        self,
        task_id: str,
        depends_on_id: str,
        dependency_type: str = "PRECEDES"
    ) -> Optional[Edge]:
        """Add a dependency between tasks."""
        if task_id not in self.tasks or depends_on_id not in self.tasks:
            return None
        
        edge_id = f"{depends_on_id}->{task_id}:{dependency_type}"
        
        edge = Edge(
            id=edge_id,
            source_id=depends_on_id,
            target_id=task_id,
            type=dependency_type,
        )
        
        self.dependencies[edge_id] = edge
        self.adjacency[depends_on_id].add(edge_id)
        self.adjacency[task_id].add(edge_id)
        
        return edge
    
    def get_ready_tasks(self) -> List[Node]:
        """Get tasks that have no unmet dependencies."""
        ready = []
        
        for task_id, task in self.tasks.items():
            # Check if all dependencies are met
            has_unmet = False
            for edge_id in self.adjacency.get(task_id, set()):
                edge = self.dependencies.get(edge_id)
                if edge and edge.target_id == task_id:
                    # This is an incoming dependency
                    source_task = self.tasks.get(edge.source_id)
                    if source_task and source_task.properties.get("status") != "completed":
                        has_unmet = True
                        break
            
            if not has_unmet:
                ready.append(task)
        
        return ready
    
    def to_dict(self) -> Dict[str, Any]:
        """Export the task graph as a dictionary."""
        return {
            "name": self.name,
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "dependencies": {did: d.to_dict() for did, d in self.dependencies.items()},
            "stats": {
                "total_tasks": len(self.tasks),
                "total_dependencies": len(self.dependencies),
            },
        }


# ─── Memory Manager ─────────────────────────────────────────────────────────

class MemoryManager:
    """
    Unified memory manager for MoA Swarm.
    
    Integrates:
    - Knowledge Graph: Long-term memory (entities, facts, relations)
    - Task Graph: Execution memory (jobs, dependencies)
    - Session Memory: Current context
    - Collective Memory: Shared across agents
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Knowledge graph for long-term memory
        self.knowledge = KnowledgeGraph(name="moa_swarm")
        
        # Task graph for execution memory
        self.tasks = TaskGraph(name="moa_tasks")
        
        # Session memory (current context)
        self.session: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "started_at": datetime.utcnow(),
            "context": {},
            "history": [],
        }
        
        # Collective memory (shared across agents)
        self.collective: Dict[str, Any] = {
            "facts": {},
            "patterns": {},
            "decisions": {},
            "learnings": {},
        }
        
        # Memory paths
        self.memory_dir = Path(self.config.get("memory_dir", "memory"))
        self.memory_dir.mkdir(exist_ok=True)
        
    def store_fact(
        self,
        entity: str,
        fact: str,
        source: str = "agent",
        confidence: float = 1.0,
        agent_id: Optional[str] = None
    ) -> Node:
        """Store a fact in the knowledge graph."""
        # Check if entity exists
        existing = self.knowledge.get_node_by_name(entity)
        
        if not existing:
            # Create entity node
            entity_node = self.knowledge.add_node(
                type=NodeType.ENTITY,
                name=entity,
                provenance=Provenance(source=source, confidence=confidence, agent_id=agent_id)
            )
        else:
            entity_node = existing
        
        # Create fact node
        fact_node = self.knowledge.add_node(
            type=NodeType.FACT,
            name=f"{entity}:{fact[:50]}",
            properties={"full_fact": fact, "entity": entity},
            provenance=Provenance(source=source, confidence=confidence, agent_id=agent_id)
        )
        
        # Link fact to entity
        self.knowledge.add_edge(
            source_id=entity_node.id,
            target_id=fact_node.id,
            type=EdgeType.RELATED_TO,
            provenance=Provenance(source=source, agent_id=agent_id)
        )
        
        # Store in collective memory
        if entity not in self.collective["facts"]:
            self.collective["facts"][entity] = []
        self.collective["facts"][entity].append({
            "fact": fact,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return fact_node
    
    def store_pattern(
        self,
        pattern_name: str,
        pattern: Dict[str, Any],
        source: str = "agent",
        agent_id: Optional[str] = None
    ) -> Node:
        """Store a learned pattern."""
        pattern_node = self.knowledge.add_node(
            type=NodeType.CONCEPT,
            name=pattern_name,
            properties=pattern,
            provenance=Provenance(source=source, agent_id=agent_id)
        )
        
        # Store in collective memory
        self.collective["patterns"][pattern_name] = {
            "pattern": pattern,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return pattern_node
    
    def store_decision(
        self,
        decision: str,
        context: Dict[str, Any],
        outcome: Optional[str] = None,
        source: str = "agent",
        agent_id: Optional[str] = None
    ) -> Node:
        """Store a decision and its context."""
        decision_node = self.knowledge.add_node(
            type=NodeType.EVENT,
            name=f"decision:{decision[:50]}",
            properties={
                "decision": decision,
                "context": context,
                "outcome": outcome,
            },
            provenance=Provenance(source=source, agent_id=agent_id)
        )
        
        # Store in collective memory
        self.collective["decisions"][decision] = {
            "context": context,
            "outcome": outcome,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return decision_node
    
    def recall(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Recall memories matching a query."""
        results = {
            "facts": [],
            "patterns": [],
            "decisions": [],
            "learnings": [],
        }
        
        # Search facts
        for entity, facts in self.collective["facts"].items():
            if query.lower() in entity.lower():
                results["facts"].extend(facts[:limit])
        
        # Search patterns
        for name, pattern in self.collective["patterns"].items():
            if query.lower() in name.lower():
                results["patterns"].append(pattern)
        
        # Search decisions
        for decision, data in self.collective["decisions"].items():
            if query.lower() in decision.lower():
                results["decisions"].append(data)
        
        return results
    
    def associate(
        self,
        entity1: str,
        entity2: str,
        relationship: str,
        weight: float = 1.0
    ) -> Optional[Edge]:
        """Create an association between two entities."""
        node1 = self.knowledge.get_node_by_name(entity1)
        node2 = self.knowledge.get_node_by_name(entity2)
        
        if not node1:
            node1 = self.knowledge.add_node(
                type=NodeType.ENTITY,
                name=entity1
            )
        
        if not node2:
            node2 = self.knowledge.add_node(
                type=NodeType.ENTITY,
                name=entity2
            )
        
        return self.knowledge.add_edge(
            source_id=node1.id,
            target_id=node2.id,
            type=relationship,
            weight=weight
        )
    
    def create_task(
        self,
        name: str,
        task_type: str = "job",
        dependencies: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Node:
        """Create a task in the task graph."""
        task = self.tasks.add_task(
            name=name,
            task_type=task_type,
            properties=properties,
            agent_id=agent_id
        )
        
        # Add dependencies
        if dependencies:
            for dep_name in dependencies:
                # Find dependency task by name
                for tid, t in self.tasks.tasks.items():
                    if t.name == dep_name:
                        self.tasks.add_dependency(task.id, tid)
                        break
        
        return task
    
    def get_ready_tasks(self) -> List[Node]:
        """Get tasks ready for execution."""
        return self.tasks.get_ready_tasks()
    
    def save_memory(self) -> None:
        """Save all memory to disk."""
        # Save knowledge graph
        self.knowledge.save(self.memory_dir / "knowledge.json")
        
        # Save task graph
        task_data = self.tasks.to_dict()
        with open(self.memory_dir / "tasks.json", "w") as f:
            json.dump(task_data, f, indent=2)
        
        # Save collective memory
        with open(self.memory_dir / "collective.json", "w") as f:
            json.dump(self.collective, f, indent=2, default=str)
        
        # Save session memory
        with open(self.memory_dir / "session.json", "w") as f:
            json.dump(self.session, f, indent=2, default=str)
    
    def load_memory(self) -> None:
        """Load all memory from disk."""
        # Load knowledge graph
        knowledge_path = self.memory_dir / "knowledge.json"
        if knowledge_path.exists():
            self.knowledge.load(str(knowledge_path))
        
        # Load task graph
        tasks_path = self.memory_dir / "tasks.json"
        if tasks_path.exists():
            with open(tasks_path, "r") as f:
                task_data = json.load(f)
            # Reconstruct task graph
            for tid, t_data in task_data.get("tasks", {}).items():
                node = Node(
                    id=t_data["id"],
                    type=t_data["type"],
                    name=t_data["name"],
                    properties=t_data.get("properties", {}),
                )
                self.tasks.tasks[tid] = node
        
        # Load collective memory
        collective_path = self.memory_dir / "collective.json"
        if collective_path.exists():
            with open(collective_path, "r") as f:
                self.collective = json.load(f)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "knowledge_graph": {
                "total_nodes": len(self.knowledge.nodes),
                "total_edges": len(self.knowledge.edges),
                "node_types": {t: len(ids) for t, ids in self.knowledge.type_index.items()},
            },
            "task_graph": {
                "total_tasks": len(self.tasks.tasks),
                "total_dependencies": len(self.tasks.dependencies),
            },
            "collective_memory": {
                "facts": len(self.collective["facts"]),
                "patterns": len(self.collective["patterns"]),
                "decisions": len(self.collective["decisions"]),
            },
            "session": {
                "id": self.session["id"],
                "started_at": self.session["started_at"].isoformat(),
                "history_length": len(self.session["history"]),
            },
        }


# ─── Singleton Memory ────────────────────────────────────────────────────────

_memory_instance: Optional[MemoryManager] = None


def get_memory(config: Optional[Dict[str, Any]] = None) -> MemoryManager:
    """Get the singleton memory manager instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = MemoryManager(config)
    return _memory_instance


def setup_memory(config: Optional[Dict[str, Any]] = None) -> MemoryManager:
    """Setup memory manager with the given configuration."""
    global _memory_instance
    _memory_instance = MemoryManager(config)
    return _memory_instance


# ─── Usage Example ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize memory manager
    memory = MemoryManager()
    
    print("=" * 60)
    print("MoA Swarm Memory System (Graph-Engineering)")
    print("=" * 60)
    
    # Store some facts
    memory.store_fact("MoA", "Mixture of Agents uses parallel proposers and aggregator", source="architecture")
    memory.store_fact("heart_bleed", "Core model call function for all LLM interactions", source="code")
    memory.store_fact("MCP", "Model Context Protocol enables external AI access", source="protocol")
    
    # Store patterns
    memory.store_pattern("MoA Workflow", {
        "phase_1": "parallel_proposers",
        "phase_2": "aggregation",
        "output": "refined_response"
    })
    
    # Store decisions
    memory.store_decision(
        "Use in-memory storage",
        {"reason": "Simplicity, no external dependencies"},
        outcome="implemented"
    )
    
    # Create associations
    memory.associate("MoA", "heart_bleed", EdgeType.USED_BY)
    memory.associate("MoA", "MCP", EdgeType.RELATED_TO)
    
    # Create tasks
    memory.create_task("Implement heart_bleed", dependencies=[])
    memory.create_task("Implement MCP server", dependencies=["Implement heart_bleed"])
    memory.create_task("Test system", dependencies=["Implement MCP server"])
    
    # Recall memories
    print("\nRecalling 'MoA':")
    results = memory.recall("MoA")
    print(f"  Facts: {len(results['facts'])}")
    print(f"  Patterns: {len(results['patterns'])}")
    
    # Get stats
    print("\nMemory Stats:")
    stats = memory.get_stats()
    print(f"  Knowledge Graph: {stats['knowledge_graph']['total_nodes']} nodes, {stats['knowledge_graph']['total_edges']} edges")
    print(f"  Task Graph: {stats['task_graph']['total_tasks']} tasks")
    print(f"  Collective: {stats['collective_memory']['facts']} facts")
    
    # Save memory
    memory.save_memory()
    print("\nMemory saved to disk!")
