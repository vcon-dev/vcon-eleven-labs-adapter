"""
Data models for ElevenLabs API responses
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ConversationStatus(str, Enum):
    """Conversation status enumeration"""

    ACTIVE = "active"
    COMPLETED = "completed"
    DONE = "done"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class ConversationParticipant(BaseModel):
    """Participant in a conversation"""

    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "participant"


class AudioRecording(BaseModel):
    """Audio recording information"""

    url: Optional[str] = None
    duration_ms: int
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"
    size_bytes: Optional[int] = None


class Transcript(BaseModel):
    """Transcript information"""

    text: str
    language: str = "en"
    confidence: Optional[float] = None


class Conversation(BaseModel):
    """Conversation model representing an agent interaction"""

    model_config = ConfigDict(use_enum_values=True)

    id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: str = "completed"  # Changed to string for flexibility with API values
    participants: List[ConversationParticipant]
    audio: Optional[AudioRecording] = None
    transcript: Optional[Transcript] = None
    metadata: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class Agent(BaseModel):
    """Agent model"""

    model_config = ConfigDict(use_enum_values=True)

    id: str
    name: str
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
