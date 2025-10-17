"""
ElevenLabs API extractor for conversation data
"""

import time
from typing import List, Optional
from datetime import datetime, timedelta
from src.models.elevenlabs_models import Agent, Conversation, ConversationParticipant
from src.logger import get_logger

try:
    from elevenlabs import ElevenLabs
except ImportError:
    ElevenLabs = None

logger = get_logger(__name__)


class ElevenLabsExtractor:
    """
    Extracts conversation data from ElevenLabs API
    """

    def __init__(
        self,
        api_key: str,
        timeout: int = 30,
        batch_size: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize ElevenLabs extractor

        Args:
            api_key: ElevenLabs API key
            timeout: Request timeout in seconds
            batch_size: Number of items to fetch per batch
            max_retries: Maximum number of retries on failure
        """
        self.api_key = api_key
        self.timeout = timeout
        self.batch_size = batch_size
        self.max_retries = max_retries

        try:
            if ElevenLabs is None:
                raise ImportError("elevenlabs package not installed")
            self.client = ElevenLabs(api_key=api_key)
        except ImportError:
            logger.error("elevenlabs package not installed")
            raise

    def list_agents(self) -> List[Agent]:
        """
        Fetch list of all agents

        Returns:
            List of Agent objects
        """
        try:
            logger.info("Fetching agents from ElevenLabs API")
            agents_data = self._retry_api_call(self._fetch_agents)

            agents = []
            for agent_data in agents_data:
                agent = self._parse_agent(agent_data)
                agents.append(agent)

            logger.info(f"Successfully fetched {len(agents)} agents")
            return agents

        except Exception as e:
            logger.error(f"Error fetching agents: {str(e)}")
            raise

    def get_agent_conversations(
        self,
        agent_id: str,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> List[Conversation]:
        """
        Fetch conversations for a specific agent

        Args:
            agent_id: Agent ID
            limit: Maximum number of conversations to fetch
            since: Only fetch conversations after this timestamp

        Returns:
            List of Conversation objects
        """
        try:
            logger.info(f"Fetching conversations for agent {agent_id}")

            conversations_data = self._retry_api_call(
                self._fetch_agent_conversations,
                agent_id=agent_id,
                limit=limit,
                since=since,
            )

            conversations = []
            for conv_data in conversations_data:
                conversation = self._parse_conversation(conv_data)
                conversations.append(conversation)

            logger.info(
                f"Successfully fetched {len(conversations)} conversations for agent {agent_id}"
            )
            return conversations

        except Exception as e:
            logger.error(f"Error fetching conversations: {str(e)}")
            raise

    def get_conversation_audio(self, conversation_id: str) -> Optional[bytes]:
        """
        Fetch audio for a specific conversation

        Args:
            conversation_id: Conversation ID

        Returns:
            Audio bytes or None if not available
        """
        try:
            logger.info(f"Fetching audio for conversation {conversation_id}")
            audio_data = self._retry_api_call(
                self._fetch_audio,
                conversation_id=conversation_id,
            )

            return audio_data

        except Exception as e:
            logger.error(f"Error fetching audio: {str(e)}")
            return None

    def _fetch_agents(self) -> List[dict]:
        """Fetch agents from API (internal)"""
        agents = []
        try:
            response = self.client.agents.list()
            if hasattr(response, "__iter__"):
                agents = list(response)
            else:
                agents = response
        except Exception as e:
            logger.warning(f"Could not fetch agents directly: {str(e)}")
            agents = []

        return agents

    def _fetch_agent_conversations(
        self,
        agent_id: str,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> List[dict]:
        """Fetch agent conversations from API (internal)"""
        conversations = []
        try:
            params = {"agent_id": agent_id}
            if limit:
                params["limit"] = limit
            if since:
                params["since"] = since.isoformat()

            response = self.client.conversations.list(**params)

            if hasattr(response, "__iter__"):
                conversations = list(response)
            else:
                conversations = response

        except Exception as e:
            logger.warning(f"Could not fetch conversations: {str(e)}")
            conversations = []

        return conversations

    def _fetch_audio(self, conversation_id: str) -> Optional[bytes]:
        """Fetch audio from API (internal)"""
        try:
            audio_data = self.client.conversations.get_audio(conversation_id)
            return audio_data
        except Exception as e:
            logger.warning(f"Could not fetch audio: {str(e)}")
            return None

    def _retry_api_call(self, func, *args, **kwargs):
        """
        Retry an API call with exponential backoff

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise

                wait_time = 2 ** attempt
                logger.warning(
                    f"API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}"
                )
                time.sleep(wait_time)

    def _parse_agent(self, agent_data: dict) -> Agent:
        """Parse agent data into Agent model"""
        return Agent(
            id=agent_data.get("id", ""),
            name=agent_data.get("name", "Unknown Agent"),
            status=agent_data.get("status", "active"),
            created_at=self._parse_datetime(agent_data.get("created_at")),
            updated_at=self._parse_datetime(agent_data.get("updated_at")),
            description=agent_data.get("description"),
            avatar_url=agent_data.get("avatar_url"),
            metadata=agent_data.get("metadata", {}),
        )

    def _parse_conversation(self, conv_data: dict) -> Conversation:
        """Parse conversation data into Conversation model"""
        participants = []
        for p in conv_data.get("participants", []):
            participants.append(
                ConversationParticipant(
                    id=p.get("id", ""),
                    name=p.get("name"),
                    email=p.get("email"),
                    phone=p.get("phone"),
                    role=p.get("role", "participant"),
                )
            )

        return Conversation(
            id=conv_data.get("id", ""),
            agent_id=conv_data.get("agent_id", ""),
            start_time=self._parse_datetime(conv_data.get("start_time")),
            end_time=self._parse_datetime(conv_data.get("end_time")),
            duration_ms=conv_data.get("duration_ms"),
            status=conv_data.get("status", "completed"),
            participants=participants,
            metadata=conv_data.get("metadata", {}),
            tags=conv_data.get("tags", []),
        )

    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string"""
        if not date_str:
            return None

        try:
            if isinstance(date_str, datetime):
                return date_str
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.warning(f"Could not parse datetime {date_str}: {str(e)}")
            return None
