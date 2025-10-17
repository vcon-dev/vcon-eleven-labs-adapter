"""
Pytest configuration and shared fixtures
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, MagicMock
from src.models.elevenlabs_models import (
    Agent,
    Conversation,
    ConversationParticipant,
    AudioRecording,
    Transcript,
    ConversationStatus,
)


@pytest.fixture
def sample_agent():
    """Sample ElevenLabs agent"""
    return Agent(
        id="agent_123",
        name="Customer Support Agent",
        status="active",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
        updated_at=datetime(2025, 1, 15, 12, 0, 0),
        description="Main customer support agent",
        metadata={"region": "us-east-1"},
    )


@pytest.fixture
def sample_participants():
    """Sample conversation participants"""
    return [
        ConversationParticipant(
            id="agent_participant_1",
            name="Sarah",
            email="sarah@company.com",
            phone="+1-555-0100",
            role="agent",
        ),
        ConversationParticipant(
            id="customer_participant_1",
            name="John Smith",
            email="john@customer.com",
            phone="+1-555-0101",
            role="customer",
        ),
    ]


@pytest.fixture
def sample_audio_recording():
    """Sample audio recording"""
    return AudioRecording(
        url="https://example.com/recordings/conv_123.wav",
        duration_ms=120000,
        sample_rate=16000,
        channels=1,
        format="wav",
        size_bytes=1920000,
    )


@pytest.fixture
def sample_transcript():
    """Sample transcript"""
    return Transcript(
        text="Hello, this is customer support. How can I help you today? I'd like to report an issue with my account.",
        language="en",
        confidence=0.95,
    )


@pytest.fixture
def sample_conversation(sample_participants, sample_audio_recording, sample_transcript):
    """Sample conversation"""
    return Conversation(
        id="conv_123",
        agent_id="agent_123",
        start_time=datetime(2025, 1, 15, 10, 0, 0),
        end_time=datetime(2025, 1, 15, 10, 2, 0),
        duration_ms=120000,
        status=ConversationStatus.COMPLETED,
        participants=sample_participants,
        audio=sample_audio_recording,
        transcript=sample_transcript,
        metadata={"campaign": "support_calls"},
        tags=["important", "resolved"],
    )


@pytest.fixture
def sample_conversation_no_audio(sample_participants, sample_transcript):
    """Sample conversation without audio"""
    return Conversation(
        id="conv_456",
        agent_id="agent_123",
        start_time=datetime(2025, 1, 15, 11, 0, 0),
        end_time=datetime(2025, 1, 15, 11, 5, 0),
        duration_ms=300000,
        status=ConversationStatus.COMPLETED,
        participants=sample_participants,
        audio=None,
        transcript=sample_transcript,
        metadata={},
        tags=[],
    )


@pytest.fixture
def mock_elevenlabs_client():
    """Mock ElevenLabs client"""
    mock_client = MagicMock()

    mock_agents = MagicMock()
    mock_agents.list.return_value = [
        {
            "id": "agent_123",
            "name": "Customer Support Agent",
            "status": "active",
            "created_at": "2025-01-01T12:00:00Z",
        }
    ]
    mock_client.agents = mock_agents

    mock_conversations = MagicMock()
    mock_conversations.list.return_value = [
        {
            "id": "conv_123",
            "agent_id": "agent_123",
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T10:02:00Z",
            "status": "completed",
            "participants": [
                {"id": "agent_1", "name": "Sarah", "role": "agent"},
                {"id": "customer_1", "name": "John", "role": "customer"},
            ],
        }
    ]
    mock_conversations.get_audio.return_value = b"mock_audio_data"
    mock_client.conversations = mock_conversations

    return mock_client


@pytest.fixture
def mock_s3_client():
    """Mock S3 client"""
    mock_s3 = MagicMock()
    mock_s3.head_bucket.return_value = {}
    mock_s3.put_object.return_value = {"ETag": '"abc123"'}
    return mock_s3


@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mock requests.post"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr("requests.post", mock_post)
    return mock_response


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file"""
    config = {
        "elevenlabs": {
            "api_key": "test_key",
            "agent_ids": ["agent_123"],
            "poll_interval": 300,
            "batch_size": 10,
            "timeout": 30,
        },
        "exporters": {
            "file": {
                "enabled": True,
                "directory": str(tmp_path / "vcons"),
                "overwrite": False,
            },
            "s3": {"enabled": False},
            "webhook": {"enabled": False},
        },
        "logging": {
            "level": "INFO",
            "file": None,
            "console": False,
            "format": "text",
        },
        "vcon": {
            "include_analysis": True,
            "include_attachments": True,
            "sign": False,
            "encryption": "none",
        },
    }

    config_file = tmp_path / "config.yml"
    with open(config_file, "w") as f:
        import yaml

        yaml.dump(config, f)

    return str(config_file)


@pytest.fixture
def fixture_agent_dict():
    """Agent fixture as dictionary"""
    return {
        "id": "agent_123",
        "name": "Test Agent",
        "status": "active",
        "created_at": "2025-01-01T12:00:00Z",
        "description": "Test agent for fixtures",
        "metadata": {"test": True},
    }


@pytest.fixture
def fixture_conversation_dict():
    """Conversation fixture as dictionary"""
    return {
        "id": "conv_123",
        "agent_id": "agent_123",
        "start_time": "2025-01-15T10:00:00Z",
        "end_time": "2025-01-15T10:02:00Z",
        "duration_ms": 120000,
        "status": "completed",
        "participants": [
            {
                "id": "agent_1",
                "name": "Agent",
                "email": "agent@test.com",
                "phone": "+1-555-0100",
                "role": "agent",
            },
            {
                "id": "customer_1",
                "name": "Customer",
                "email": "customer@test.com",
                "phone": "+1-555-0101",
                "role": "customer",
            },
        ],
        "metadata": {"test": True},
        "tags": ["test"],
    }
