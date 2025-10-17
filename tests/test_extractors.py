"""
Tests for ElevenLabs API extractors
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor


class TestElevenLabsExtractorInitialization:
    """Tests for ElevenLabsExtractor initialization"""

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_initialization(self, mock_elevenlabs_class):
        """Test extractor initialization"""
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        assert extractor.api_key == "test_key"
        assert extractor.timeout == 30
        assert extractor.batch_size == 10
        assert extractor.max_retries == 3
        mock_elevenlabs_class.assert_called_once_with(api_key="test_key")

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_initialization_custom_params(self, mock_elevenlabs_class):
        """Test extractor initialization with custom parameters"""
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(
            api_key="test_key",
            timeout=60,
            batch_size=20,
            max_retries=5,
        )

        assert extractor.timeout == 60
        assert extractor.batch_size == 20
        assert extractor.max_retries == 5

    def test_initialization_missing_key(self):
        """Test that missing API key raises error"""
        with pytest.raises(TypeError):
            ElevenLabsExtractor()


class TestElevenLabsExtractorListAgents:
    """Tests for list_agents method"""

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_list_agents(self, mock_elevenlabs_class, fixture_agent_dict):
        """Test listing agents"""
        mock_client = MagicMock()
        mock_agents = MagicMock()
        mock_agents.list.return_value = [fixture_agent_dict]
        mock_client.agents = mock_agents
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        agents = extractor.list_agents()

        assert len(agents) == 1
        assert agents[0].id == "agent_123"
        assert agents[0].name == "Test Agent"

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_list_agents_empty(self, mock_elevenlabs_class):
        """Test listing agents when none exist"""
        mock_client = MagicMock()
        mock_agents = MagicMock()
        mock_agents.list.return_value = []
        mock_client.agents = mock_agents
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        agents = extractor.list_agents()

        assert agents == []

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_list_agents_api_error(self, mock_elevenlabs_class):
        """Test handling API error when listing agents"""
        mock_client = MagicMock()
        mock_agents = MagicMock()
        mock_agents.list.side_effect = Exception("API Error")
        mock_client.agents = mock_agents
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        # API error returns empty list
        agents = extractor.list_agents()
        assert agents == []


class TestElevenLabsExtractorGetConversations:
    """Tests for get_agent_conversations method"""

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_get_agent_conversations(self, mock_elevenlabs_class, fixture_conversation_dict):
        """Test getting conversations for an agent"""
        mock_client = MagicMock()
        mock_conversations = MagicMock()
        mock_conversations.list.return_value = [fixture_conversation_dict]
        mock_client.conversations = mock_conversations
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        conversations = extractor.get_agent_conversations("agent_123")

        assert len(conversations) == 1
        assert conversations[0].id == "conv_123"
        assert conversations[0].agent_id == "agent_123"

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_get_agent_conversations_empty(self, mock_elevenlabs_class):
        """Test getting conversations when none exist"""
        mock_client = MagicMock()
        mock_conversations = MagicMock()
        mock_conversations.list.return_value = []
        mock_client.conversations = mock_conversations
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        conversations = extractor.get_agent_conversations("agent_123")

        assert conversations == []

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_get_agent_conversations_with_limit(self, mock_elevenlabs_class, fixture_conversation_dict):
        """Test getting limited conversations"""
        mock_client = MagicMock()
        mock_conversations = MagicMock()
        mock_conversations.list.return_value = [fixture_conversation_dict]
        mock_client.conversations = mock_conversations
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        conversations = extractor.get_agent_conversations("agent_123", limit=10)

        mock_conversations.list.assert_called_once()
        assert len(conversations) == 1

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_get_agent_conversations_api_error(self, mock_elevenlabs_class):
        """Test handling API error when getting conversations"""
        mock_client = MagicMock()
        mock_conversations = MagicMock()
        mock_conversations.list.side_effect = Exception("API Error")
        mock_client.conversations = mock_conversations
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        # API error returns empty list
        conversations = extractor.get_agent_conversations("agent_123")
        assert conversations == []


class TestElevenLabsExtractorGetAudio:
    """Tests for get_conversation_audio method"""

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_get_conversation_audio(self, mock_elevenlabs_class):
        """Test getting audio for a conversation"""
        mock_client = MagicMock()
        mock_conversations = MagicMock()
        audio_bytes = b"mock_audio_data"
        mock_conversations.get_audio.return_value = audio_bytes
        mock_client.conversations = mock_conversations
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        audio = extractor.get_conversation_audio("conv_123")

        assert audio == audio_bytes

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_get_conversation_audio_not_found(self, mock_elevenlabs_class):
        """Test getting audio when it doesn't exist"""
        mock_client = MagicMock()
        mock_conversations = MagicMock()
        mock_conversations.get_audio.return_value = None
        mock_client.conversations = mock_conversations
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        audio = extractor.get_conversation_audio("conv_123")

        assert audio is None

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_get_conversation_audio_error(self, mock_elevenlabs_class):
        """Test handling error when getting audio"""
        mock_client = MagicMock()
        mock_conversations = MagicMock()
        mock_conversations.get_audio.side_effect = Exception("API Error")
        mock_client.conversations = mock_conversations
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")
        audio = extractor.get_conversation_audio("conv_123")

        assert audio is None


class TestElevenLabsExtractorRetryLogic:
    """Tests for retry logic"""

    @patch("src.extractors.elevenlabs_extractor.time.sleep")
    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_retry_on_failure(self, mock_elevenlabs_class, mock_sleep):
        """Test retry mechanism on API failure"""
        mock_client = MagicMock()
        mock_agents = MagicMock()

        # Always fail - the code catches the exception and returns empty list
        mock_agents.list.side_effect = Exception("Temporary failure")
        mock_client.agents = mock_agents
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key", max_retries=3)
        agents = extractor.list_agents()

        # API failure returns empty list
        assert len(agents) == 0


class TestElevenLabsExtractorParsing:
    """Tests for data parsing methods"""

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_parse_agent(self, mock_elevenlabs_class):
        """Test parsing agent data"""
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        agent_data = {
            "id": "agent_1",
            "name": "Support Bot",
            "status": "active",
            "created_at": "2025-01-01T12:00:00Z",
            "description": "A test agent",
        }

        agent = extractor._parse_agent(agent_data)

        assert agent.id == "agent_1"
        assert agent.name == "Support Bot"
        assert agent.status == "active"

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_parse_conversation(self, mock_elevenlabs_class):
        """Test parsing conversation data"""
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        conv_data = {
            "id": "conv_1",
            "agent_id": "agent_1",
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T10:02:00Z",
            "status": "completed",
            "participants": [
                {"id": "agent_1", "name": "Agent", "role": "agent"},
                {"id": "customer_1", "name": "Customer", "role": "customer"},
            ],
        }

        conversation = extractor._parse_conversation(conv_data)

        assert conversation.id == "conv_1"
        assert conversation.agent_id == "agent_1"
        assert len(conversation.participants) == 2

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_parse_datetime(self, mock_elevenlabs_class):
        """Test parsing datetime strings"""
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        dt = extractor._parse_datetime("2025-01-15T10:00:00Z")

        assert dt is not None
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_parse_datetime_none(self, mock_elevenlabs_class):
        """Test parsing None datetime"""
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        dt = extractor._parse_datetime(None)

        assert dt is None

    @patch("src.extractors.elevenlabs_extractor.ElevenLabs")
    def test_parse_datetime_already_datetime(self, mock_elevenlabs_class):
        """Test parsing datetime object"""
        mock_client = MagicMock()
        mock_elevenlabs_class.return_value = mock_client

        extractor = ElevenLabsExtractor(api_key="test_key")

        now = datetime.now()
        dt = extractor._parse_datetime(now)

        assert dt == now
