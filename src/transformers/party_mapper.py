"""
Maps ElevenLabs conversation participants to vCon Party objects
"""

from typing import List, Dict
from vcon.party import Party
from src.models.elevenlabs_models import Conversation
from src.logger import get_logger

logger = get_logger(__name__)


class PartyMapper:
    """Maps conversation participants to vCon Party objects"""

    @staticmethod
    def map_parties(conversation: Conversation) -> List[Party]:
        """
        Convert conversation participants to vCon Party objects

        Args:
            conversation: Conversation object with participants

        Returns:
            List of vCon Party objects
        """
        parties = []

        for participant in conversation.participants:
            try:
                party = Party(
                    name=participant.name or "Unknown",
                    tel=participant.phone,
                    mailto=participant.email,
                    role=participant.role or "participant",
                    uuid=participant.id,
                )
                parties.append(party)
                logger.debug(
                    f"Mapped participant {participant.id} ({participant.name}) as {participant.role}"
                )

            except Exception as e:
                logger.error(f"Error mapping participant {participant.id}: {str(e)}")
                raise

        if not parties:
            logger.warning("No parties could be mapped from conversation")

        return parties

    @staticmethod
    def get_party_index(parties: List[Party], uuid: str) -> int:
        """
        Get the index of a party by UUID

        Args:
            parties: List of Party objects
            uuid: UUID to search for

        Returns:
            Index of the party, or -1 if not found
        """
        for i, party in enumerate(parties):
            if party.uuid == uuid:
                return i

        return -1

    @staticmethod
    def get_agent_party_index(parties: List[Party]) -> int:
        """
        Get the index of the agent party (first agent role found)

        Args:
            parties: List of Party objects

        Returns:
            Index of agent party, or first party if no agent role found
        """
        for i, party in enumerate(parties):
            if party.role == "agent":
                return i

        return 0 if parties else -1

    @staticmethod
    def get_customer_party_index(parties: List[Party]) -> int:
        """
        Get the index of the customer party (first customer role found)

        Args:
            parties: List of Party objects

        Returns:
            Index of customer party, or last party if no customer role found
        """
        for i, party in enumerate(parties):
            if party.role == "customer" or party.role == "user":
                return i

        return len(parties) - 1 if parties else -1
