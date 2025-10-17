"""
Builds complete vCon objects from conversation data
"""

from datetime import datetime, timezone
from vcon import Vcon
from src.models.elevenlabs_models import Conversation
from src.transformers.party_mapper import PartyMapper
from src.transformers.dialog_processor import DialogProcessor
from src.logger import get_logger

logger = get_logger(__name__)


class VconBuilder:
    """Builds complete vCon objects from conversation data"""

    def __init__(
        self,
        include_analysis: bool = True,
        include_attachments: bool = True,
    ):
        """
        Initialize vCon builder

        Args:
            include_analysis: Whether to include analysis section
            include_attachments: Whether to include attachments
        """
        self.include_analysis = include_analysis
        self.include_attachments = include_attachments

    def build_vcon(self, conversation: Conversation) -> Vcon:
        """
        Build a complete vCon from a conversation

        Args:
            conversation: Conversation object to convert

        Returns:
            Complete Vcon object
        """
        try:
            logger.info(f"Building vCon for conversation {conversation.id}")

            vcon = Vcon.build_new(created_at=datetime.now(timezone.utc))

            self._add_parties(vcon, conversation)
            self._add_dialogs(vcon, conversation)
            self._add_metadata(vcon, conversation)

            if self.include_attachments:
                self._add_attachments(vcon, conversation)

            if self.include_analysis:
                self._add_analysis(vcon, conversation)

            self._add_tags(vcon, conversation)

            is_valid, errors = vcon.is_valid()
            if not is_valid:
                logger.warning(f"Generated vCon has validation errors: {errors}")
            else:
                logger.info(f"Successfully built vCon {vcon.uuid}")

            return vcon

        except Exception as e:
            logger.error(f"Error building vCon: {str(e)}")
            raise

    def _add_parties(self, vcon: Vcon, conversation: Conversation):
        """Add parties to vCon"""
        try:
            parties = PartyMapper.map_parties(conversation)
            logger.debug(f"Mapped {len(parties)} parties from conversation")

            for party in parties:
                vcon.add_party(party)

            logger.debug(f"Added {len(parties)} parties to vCon")

        except Exception as e:
            logger.error(f"Error adding parties: {str(e)}")
            raise

    def _add_dialogs(self, vcon: Vcon, conversation: Conversation):
        """Add dialogs to vCon"""
        try:
            # vcon.parties is a list of Party objects or dicts
            party_indices = {}
            for i, party in enumerate(vcon.parties):
                if isinstance(party, dict):
                    # Get uuid from dict representation
                    party_uuid = party.get('uuid') or party.get('id')
                    if party_uuid:
                        party_indices[party_uuid] = i
                else:
                    # Party object
                    if hasattr(party, 'uuid') and party.uuid:
                        party_indices[party.uuid] = i

            dialogs = DialogProcessor.process_conversation_dialogs(
                conversation,
                party_indices,
                include_transcript=True,
            )

            for dialog in dialogs:
                vcon.add_dialog(dialog)

            logger.debug(f"Added {len(dialogs)} dialogs to vCon")

        except Exception as e:
            logger.error(f"Error adding dialogs: {str(e)}")
            raise

    def _add_metadata(self, vcon: Vcon, conversation: Conversation):
        """Add metadata to vCon"""
        try:
            # Subject and summary are read-only in vCon, use tags instead
            if conversation.start_time:
                vcon.started_at = conversation.start_time.isoformat()

            if conversation.end_time:
                vcon.ended_at = conversation.end_time.isoformat()

            logger.debug("Added metadata to vCon")

        except Exception as e:
            logger.error(f"Error adding metadata: {str(e)}")

    def _add_attachments(self, vcon: Vcon, conversation: Conversation):
        """Add attachments to vCon"""
        try:
            attachment_data = {
                "type": "conversation_metadata",
                "conversation_id": conversation.id,
                "agent_id": conversation.agent_id,
                "status": conversation.status,
                "duration_ms": conversation.duration_ms,
            }

            if conversation.metadata:
                attachment_data["metadata"] = conversation.metadata

            import json
            vcon.add_attachment(
                type="call_record",
                body=json.dumps(attachment_data),
                encoding="none",
            )

            logger.debug("Added attachments to vCon")

        except Exception as e:
            logger.error(f"Error adding attachments: {str(e)}")

    def _add_analysis(self, vcon: Vcon, conversation: Conversation):
        """Add analysis to vCon"""
        try:
            import json

            # Add structured transcript with turns if available
            if hasattr(conversation, '_transcript_data') and conversation._transcript_data:
                transcript_data = conversation._transcript_data

                # Add transcript analysis with full structured data
                analysis_data = {
                    "type": "transcript",
                    "full_text": transcript_data.get("full_text", ""),
                    "language": "en",
                    "turns": transcript_data.get("transcript_turns", [])
                }

                vcon.add_analysis(
                    type="transcript",
                    dialog=0,  # First dialog (audio)
                    vendor="elevenlabs",
                    body=json.dumps(analysis_data),
                    encoding="none",
                )

                # Add call analysis if available
                if transcript_data.get("analysis"):
                    analysis_info = transcript_data["analysis"]
                    call_analysis_data = {
                        "type": "summary",
                        "summary": analysis_info.get("summary"),
                        "title": analysis_info.get("title"),
                        "call_successful": analysis_info.get("call_successful")
                    }

                    vcon.add_analysis(
                        type="summary",
                        dialog=0,
                        vendor="elevenlabs",
                        body=json.dumps(call_analysis_data),
                        encoding="none",
                    )

                logger.debug("Added transcript and analysis to vCon")

            elif conversation.transcript:
                # Fallback to simple transcript
                analysis_data = {
                    "type": "transcript",
                    "text": conversation.transcript.text,
                    "language": conversation.transcript.language,
                }

                if conversation.transcript.confidence:
                    analysis_data["confidence"] = conversation.transcript.confidence

                vcon.add_analysis(
                    type="transcript",
                    dialog=0,
                    vendor="elevenlabs",
                    body=json.dumps(analysis_data),
                    encoding="none",
                )

                logger.debug("Added simple transcript to vCon")

        except Exception as e:
            logger.error(f"Error adding analysis: {str(e)}")

    def _add_tags(self, vcon: Vcon, conversation: Conversation):
        """Add tags to vCon"""
        try:
            vcon.add_tag("source", "elevenlabs")
            vcon.add_tag("conversation_id", conversation.id)
            vcon.add_tag("agent_id", conversation.agent_id)
            vcon.add_tag("status", conversation.status)

            for tag in conversation.tags:
                vcon.add_tag("user_tag", tag)

            logger.debug("Added tags to vCon")

        except Exception as e:
            logger.error(f"Error adding tags: {str(e)}")
