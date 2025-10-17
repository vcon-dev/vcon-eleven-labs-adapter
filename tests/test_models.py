"""
Tests for ElevenLabs data models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.models.elevenlabs_models import (
    Agent,
    Conversation,
    ConversationParticipant,
    AudioRecording,
    Transcript,
    ConversationStatus,
)


class TestConversationStatus:
    """Tests for ConversationStatus enum"""

    def test_status_values(self):
        """Test that all status values are defined"""
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.COMPLETED == "completed"
        assert ConversationStatus.FAILED == "failed"
        assert ConversationStatus.INTERRUPTED == "interrupted"


class TestConversationParticipant:
    """Tests for ConversationParticipant model"""

    def test_create_participant_minimal(self):
        """Test creating participant with minimal fields"""
        participant = ConversationParticipant(id="user_1")

        assert participant.id == "user_1"
        assert participant.name is None
        assert participant.role == "participant"

    def test_create_participant_full(self):
        """Test creating participant with all fields"""
        participant = ConversationParticipant(
            id="agent_1",
            name="John Doe",
            email="john@test.com",
            phone="+1-555-0100",
            role="agent",
        )

        assert participant.id == "agent_1"
        assert participant.name == "John Doe"
        assert participant.email == "john@test.com"
        assert participant.phone == "+1-555-0100"
        assert participant.role == "agent"

    def test_participant_default_role(self):
        """Test that default role is 'participant'"""
        participant = ConversationParticipant(id="user_1", name="Test")

        assert participant.role == "participant"


class TestAudioRecording:
    """Tests for AudioRecording model"""

    def test_create_audio_minimal(self):
        """Test creating audio recording with minimal fields"""
        audio = AudioRecording(duration_ms=60000)

        assert audio.duration_ms == 60000
        assert audio.url is None
        assert audio.format == "wav"
        assert audio.channels == 1

    def test_create_audio_full(self):
        """Test creating audio recording with all fields"""
        audio = AudioRecording(
            url="https://example.com/audio.wav",
            duration_ms=120000,
            sample_rate=16000,
            channels=2,
            format="mp3",
            size_bytes=1920000,
        )

        assert audio.url == "https://example.com/audio.wav"
        assert audio.duration_ms == 120000
        assert audio.sample_rate == 16000
        assert audio.channels == 2
        assert audio.format == "mp3"
        assert audio.size_bytes == 1920000

    def test_audio_default_values(self):
        """Test default values for audio recording"""
        audio = AudioRecording(duration_ms=30000)

        assert audio.sample_rate == 16000
        assert audio.channels == 1
        assert audio.format == "wav"


class TestTranscript:
    """Tests for Transcript model"""

    def test_create_transcript_minimal(self):
        """Test creating transcript with minimal fields"""
        transcript = Transcript(text="Hello world")

        assert transcript.text == "Hello world"
        assert transcript.language == "en"
        assert transcript.confidence is None

    def test_create_transcript_full(self):
        """Test creating transcript with all fields"""
        transcript = Transcript(
            text="This is a test transcript",
            language="es",
            confidence=0.98,
        )

        assert transcript.text == "This is a test transcript"
        assert transcript.language == "es"
        assert transcript.confidence == 0.98

    def test_transcript_default_language(self):
        """Test that default language is 'en'"""
        transcript = Transcript(text="Test")

        assert transcript.language == "en"


class TestConversation:
    """Tests for Conversation model"""

    def test_create_conversation_minimal(self):
        """Test creating conversation with minimal fields"""
        now = datetime.now()
        conversation = Conversation(
            id="conv_1",
            agent_id="agent_1",
            start_time=now,
            participants=[],
        )

        assert conversation.id == "conv_1"
        assert conversation.agent_id == "agent_1"
        assert conversation.start_time == now
        assert conversation.status == "completed"
        assert conversation.participants == []

    def test_create_conversation_full(self, sample_participants, sample_audio_recording, sample_transcript):
        """Test creating conversation with all fields"""
        start = datetime(2025, 1, 15, 10, 0, 0)
        end = datetime(2025, 1, 15, 10, 2, 0)

        conversation = Conversation(
            id="conv_1",
            agent_id="agent_1",
            start_time=start,
            end_time=end,
            duration_ms=120000,
            status=ConversationStatus.COMPLETED,
            participants=sample_participants,
            audio=sample_audio_recording,
            transcript=sample_transcript,
            metadata={"campaign": "support"},
            tags=["important"],
        )

        assert conversation.id == "conv_1"
        assert conversation.agent_id == "agent_1"
        assert conversation.start_time == start
        assert conversation.end_time == end
        assert conversation.duration_ms == 120000
        assert len(conversation.participants) == 2
        assert conversation.audio is not None
        assert conversation.transcript is not None
        assert conversation.metadata == {"campaign": "support"}
        assert conversation.tags == ["important"]

    def test_conversation_optional_fields(self):
        """Test that optional fields can be None"""
        now = datetime.now()
        conversation = Conversation(
            id="conv_1",
            agent_id="agent_1",
            start_time=now,
            participants=[],
        )

        assert conversation.end_time is None
        assert conversation.duration_ms is None
        assert conversation.audio is None
        assert conversation.transcript is None


class TestAgent:
    """Tests for Agent model"""

    def test_create_agent_minimal(self):
        """Test creating agent with minimal fields"""
        now = datetime.now()
        agent = Agent(
            id="agent_1",
            name="Support Bot",
            created_at=now,
        )

        assert agent.id == "agent_1"
        assert agent.name == "Support Bot"
        assert agent.status == "active"
        assert agent.created_at == now

    def test_create_agent_full(self):
        """Test creating agent with all fields"""
        created = datetime(2025, 1, 1, 12, 0, 0)
        updated = datetime(2025, 1, 15, 12, 0, 0)

        agent = Agent(
            id="agent_1",
            name="Support Bot",
            status="inactive",
            created_at=created,
            updated_at=updated,
            description="Test agent",
            avatar_url="https://example.com/avatar.png",
            metadata={"version": "2.0"},
        )

        assert agent.id == "agent_1"
        assert agent.name == "Support Bot"
        assert agent.status == "inactive"
        assert agent.created_at == created
        assert agent.updated_at == updated
        assert agent.description == "Test agent"
        assert agent.avatar_url == "https://example.com/avatar.png"
        assert agent.metadata == {"version": "2.0"}

    def test_agent_default_values(self):
        """Test default values for agent"""
        now = datetime.now()
        agent = Agent(
            id="agent_1",
            name="Bot",
            created_at=now,
        )

        assert agent.status == "active"
        assert agent.updated_at is None
        assert agent.description is None
        assert agent.avatar_url is None
        assert agent.metadata == {}


class TestModelValidation:
    """Tests for model validation"""

    def test_participant_validation_missing_id(self):
        """Test that ConversationParticipant requires id"""
        with pytest.raises(ValidationError):
            ConversationParticipant()

    def test_audio_validation_missing_duration(self):
        """Test that AudioRecording requires duration_ms"""
        with pytest.raises(ValidationError):
            AudioRecording()

    def test_transcript_validation_missing_text(self):
        """Test that Transcript requires text"""
        with pytest.raises(ValidationError):
            Transcript()

    def test_conversation_validation_missing_required(self):
        """Test that Conversation requires required fields"""
        with pytest.raises(ValidationError):
            Conversation(id="conv_1")

    def test_agent_validation_missing_required(self):
        """Test that Agent requires required fields"""
        with pytest.raises(ValidationError):
            Agent(id="agent_1", name="Bot")


class TestModelSerialization:
    """Tests for model serialization"""

    def test_agent_dict(self, sample_agent):
        """Test converting agent to dict"""
        agent_dict = sample_agent.model_dump()

        assert agent_dict["id"] == "agent_123"
        assert agent_dict["name"] == "Customer Support Agent"
        assert "created_at" in agent_dict

    def test_conversation_dict(self, sample_conversation):
        """Test converting conversation to dict"""
        conv_dict = sample_conversation.model_dump()

        assert conv_dict["id"] == "conv_123"
        assert conv_dict["agent_id"] == "agent_123"
        assert "participants" in conv_dict
        assert len(conv_dict["participants"]) == 2

    def test_participant_dict(self, sample_participants):
        """Test converting participant to dict"""
        participant = sample_participants[0]
        participant_dict = participant.model_dump()

        assert participant_dict["id"] == "agent_participant_1"
        assert participant_dict["name"] == "Sarah"
        assert participant_dict["role"] == "agent"
