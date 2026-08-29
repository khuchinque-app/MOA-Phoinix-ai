"""
models.py — Pydantic models for MoA Swarm Architecture

Provides type-safe data structures for API requests, responses,
and internal communication between agents.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, validator


# ─── Enums ─────────────────────────────────────────────────────────────────────

class MessageRole(str, Enum):
    """Message roles in conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ReasoningEffort(str, Enum):
    """Reasoning effort levels for model calls."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelProvider(str, Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GLM = "glm"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRole(str, Enum):
    """Agent roles in the swarm."""
    PROPOSER = "proposer"
    AGGREGATOR = "aggregator"
    BROWSER = "browser"
    DESKTOP = "desktop"
    SEARCH = "search"
    VISION = "vision"


# ─── Message Models ───────────────────────────────────────────────────────────

class Message(BaseModel):
    """A single message in a conversation."""
    role: MessageRole
    content: str
    
    class Config:
        use_enum_values = True


class Conversation(BaseModel):
    """A conversation consisting of multiple messages."""
    messages: List[Message] = []
    metadata: Dict[str, Any] = {}
    
    def add_message(self, role: MessageRole, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message content."""
        for msg in reversed(self.messages):
            if msg.role == MessageRole.USER:
                return msg.content
        return None
    
    def to_api_format(self) -> List[Dict[str, str]]:
        """Convert to API-compatible format."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]


# ─── Request Models ───────────────────────────────────────────────────────────

class ModelCallRequest(BaseModel):
    """Request for a single model call."""
    messages: List[Message]
    model: str = "glm-4.7-flash"
    reasoning_effort: ReasoningEffort = ReasoningEffort.NONE
    max_tokens: int = 400
    temperature: float = 0.7
    timeout: int = 30
    
    @validator("messages")
    def validate_messages(cls, v):
        """Ensure at least one message is provided."""
        if not v:
            raise ValueError("At least one message is required")
        return v
    
    @validator("temperature")
    def validate_temperature(cls, v):
        """Ensure temperature is in valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @validator("max_tokens")
    def validate_max_tokens(cls, v):
        """Ensure max_tokens is positive."""
        if v < 1:
            raise ValueError("max_tokens must be at least 1")
        return v
    
    def to_api_payload(self) -> Dict[str, Any]:
        """Convert to API payload format."""
        return {
            "model": self.model,
            "reasoning_effort": self.reasoning_effort.value,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": msg.role if isinstance(msg.role, str) else msg.role.value, "content": msg.content} for msg in self.messages],
        }


class BatchCallRequest(BaseModel):
    """Request for multiple parallel model calls."""
    tasks: List[ModelCallRequest]
    
    @validator("tasks")
    def validate_tasks(cls, v):
        """Ensure at least one task is provided."""
        if not v:
            raise ValueError("At least one task is required")
        return v


class AggregationRequest(BaseModel):
    """Request for aggregating multiple responses."""
    proposer_responses: List[Dict[str, Any]]
    aggregator_model: str = "claude-3-opus"
    aggregator_max_tokens: int = 800
    aggregator_temperature: float = 0.3
    
    @validator("proposer_responses")
    def validate_proposer_responses(cls, v):
        """Ensure at least one proposer response is provided."""
        if not v:
            raise ValueError("At least one proposer response is required")
        return v


# ─── Response Models ──────────────────────────────────────────────────────────

class ResponseMetadata(BaseModel):
    """Metadata attached to every API response."""
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    provider: str = ""
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Choice(BaseModel):
    """A single choice from the model response."""
    index: int = 0
    message: Message
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ModelCallResponse(BaseModel):
    """Response from a single model call."""
    id: Optional[str] = None
    object: str = "chat.completion"
    created: Optional[int] = None
    model: str = ""
    choices: List[Choice] = []
    usage: Usage = Usage()
    metadata: Optional[ResponseMetadata] = None
    error: Optional[str] = None
    
    @property
    def content(self) -> str:
        """Extract content from the first choice."""
        if self.choices and len(self.choices) > 0:
            return self.choices[0].message.content
        return ""
    
    @property
    def is_error(self) -> bool:
        """Check if this response represents an error."""
        return self.error is not None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], metadata: Optional[ResponseMetadata] = None) -> "ModelCallResponse":
        """Create from raw API response dict."""
        choices = []
        for choice_data in data.get("choices", []):
            message_data = choice_data.get("message", {})
            choices.append(
                Choice(
                    index=choice_data.get("index", 0),
                    message=Message(
                        role=message_data.get("role", "assistant"),
                        content=message_data.get("content", ""),
                    ),
                    finish_reason=choice_data.get("finish_reason"),
                )
            )
        
        usage_data = data.get("usage", {})
        
        return cls(
            id=data.get("id"),
            object=data.get("object", "chat.completion"),
            created=data.get("created"),
            model=data.get("model", ""),
            choices=choices,
            usage=Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            ),
            metadata=metadata,
            error=data.get("error"),
        )


class BatchCallResponse(BaseModel):
    """Response from multiple parallel model calls."""
    responses: List[ModelCallResponse]
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    
    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency across responses."""
        if not self.responses:
            return 0.0
        latencies = [r.metadata.latency_ms if r.metadata else 0.0 for r in self.responses]
        return sum(latencies) / len(latencies)


class AggregationResponse(BaseModel):
    """Response from aggregation."""
    final_response: ModelCallResponse
    proposer_count: int = 0
    proposer_models: List[str] = []
    aggregation_latency_ms: float = 0.0


# ─── Task Models ──────────────────────────────────────────────────────────────

class Task(BaseModel):
    """A task to be executed by the swarm."""
    id: str
    input: str
    role: AgentRole = AgentRole.PROPOSER
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    @validator("input")
    def validate_input(cls, v):
        """Ensure input is not empty."""
        if not v.strip():
            raise ValueError("Task input cannot be empty")
        return v


class Pipeline(BaseModel):
    """A complete MoA pipeline configuration."""
    id: str
    input_message: str
    proposer_configs: List[Dict[str, Any]]
    aggregator_config: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[AggregationResponse] = None
    error: Optional[str] = None


# ─── Agent Models ─────────────────────────────────────────────────────────────

class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    id: str
    role: AgentRole
    model: str = "glm-4.7-flash"
    max_tokens: int = 400
    temperature: float = 0.7
    timeout: int = 30
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AgentStatus(BaseModel):
    """Status of a running agent."""
    agent_id: str
    role: AgentRole
    status: TaskStatus
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)


# ─── Health Models ────────────────────────────────────────────────────────────

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    components: Dict[str, str] = {}
    uptime_seconds: float = 0.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if the system is healthy."""
        return self.status == "healthy"


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example: Create a model call request
    request = ModelCallRequest(
        messages=[
            Message(role=MessageRole.USER, content="Hello, how are you?")
        ],
        model="glm-4.7-flash",
        max_tokens=100,
    )
    
    print("Request:")
    print(request.json(indent=2))
    
    # Example: Create a conversation
    conversation = Conversation()
    conversation.add_message(MessageRole.SYSTEM, "You are a helpful assistant.")
    conversation.add_message(MessageRole.USER, "What is MoA?")
    
    print("\nConversation:")
    print(conversation.json(indent=2))
    
    # Example: Create a task
    task = Task(
        id="task-001",
        input="Review this code for security issues",
        role=AgentRole.PROPOSER,
    )
    
    print("\nTask:")
    print(task.json(indent=2))
