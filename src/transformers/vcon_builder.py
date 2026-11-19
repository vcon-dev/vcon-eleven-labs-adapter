"""
Builds complete vCon objects from conversation data (vCon core-05, syntax 0.5.0)

Each ElevenLabs conversation is one Session (index 0): its `parties` are the
participants (receivers), in the order the API lists them. Dialogs (the
recording and the transcript text) are listed by that Session and carry their
contributors. Attachments are scoped with `party` plus `session`; analysis
points at the Dialog it was derived from. `encoding: "json"` bodies are JSON
values, not strings.
"""

from datetime import datetime, timezone
from typing import Optional
from vcon import Vcon
from vcon.session import Session
from src.models.elevenlabs_models import Conversation
from src.transformers.party_mapper import PartyMapper
from src.transformers.dialog_processor import DialogProcessor
from src.logger import get_logger

logger = get_logger(__name__)

VCON_SYNTAX = "0.5.0"


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
            session = self._add_session(vcon, conversation)
            dialog_indices = self._add_dialogs(vcon, conversation, session)

            if self.include_attachments:
                self._add_attachments(vcon, conversation, session)

            if self.include_analysis:
                self._add_analysis(vcon, conversation, dialog_indices, session)

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

    def _add_session(self, vcon: Vcon, conversation: Conversation) -> int:
        """Add the conversation's Session; its parties are the receivers."""
        duration = None
        if conversation.duration_ms is not None:
            duration = conversation.duration_ms / 1000
        elif conversation.end_time:
            duration = (conversation.end_time - conversation.start_time).total_seconds()

        return vcon.add_session(
            Session(
                start=conversation.start_time.isoformat(),
                duration=duration,
                parties=list(range(len(vcon.parties))) or None,
            )
        )

    def _party_indices(self, vcon: Vcon) -> dict:
        """Map each party's uuid (the ElevenLabs participant id) to its index."""
        party_indices = {}
        for i, party in enumerate(vcon.parties):
            if isinstance(party, dict):
                party_uuid = party.get('uuid') or party.get('id')
            else:
                party_uuid = getattr(party, 'uuid', None)
            if party_uuid:
                party_indices[party_uuid] = i
        return party_indices

    def _add_dialogs(self, vcon: Vcon, conversation: Conversation, session: int) -> dict:
        """Add dialogs to vCon and the Session; return their indices by type."""
        try:
            dialogs = DialogProcessor.process_conversation_dialogs(
                conversation,
                self._party_indices(vcon),
                include_transcript=True,
            )

            indices = {}
            for dialog in dialogs:
                index = vcon.add_dialog(dialog, session=session)
                indices.setdefault(dialog.type, index)

            logger.debug(f"Added {len(dialogs)} dialogs to vCon")
            return indices

        except Exception as e:
            logger.error(f"Error adding dialogs: {str(e)}")
            raise

    def _agent_party(self, vcon: Vcon) -> int:
        """Index of the agent party (the party that supplies the metadata),
        or 0 when no party has the agent role."""
        for i, party in enumerate(vcon.parties):
            role = party.get("role") if isinstance(party, dict) else getattr(party, "role", None)
            if role == "agent":
                return i
        return 0

    def _add_attachments(self, vcon: Vcon, conversation: Conversation, session: int):
        """Add attachments to vCon"""
        try:
            if not vcon.parties:
                logger.debug("No parties; skipping call_record attachment")
                return

            attachment_data = {
                "type": "conversation_metadata",
                "conversation_id": conversation.id,
                "agent_id": conversation.agent_id,
                "status": conversation.status,
                "duration_ms": conversation.duration_ms,
            }

            if conversation.metadata:
                attachment_data["metadata"] = conversation.metadata

            vcon.add_attachment(
                purpose="call_record",
                body=attachment_data,
                encoding="json",
                mediatype="application/json",
                start=conversation.start_time.isoformat(),
                party=self._agent_party(vcon),
                session=session,
            )

            logger.debug("Added attachments to vCon")

        except Exception as e:
            logger.error(f"Error adding attachments: {str(e)}")

    def _add_analysis(
        self, vcon: Vcon, conversation: Conversation, dialog_indices: dict, session: int
    ):
        """Add analysis to vCon"""
        try:
            # The analysis is derived from the conversation: point at the
            # recording when there is one, else the transcript text Dialog,
            # else the Session.
            source_dialog: Optional[int] = dialog_indices.get(
                "recording", dialog_indices.get("text")
            )
            scope = {"dialog": source_dialog} if source_dialog is not None else {"sessions": session}

            def add(type_: str, body: dict) -> None:
                vcon.add_analysis(
                    type=type_,
                    vendor="elevenlabs",
                    body=body,
                    encoding="json",
                    mediatype="application/json",
                    **scope,
                )

            # Add structured transcript with turns if available
            transcript_data = getattr(conversation, '_transcript_data', None)
            if transcript_data:
                add("transcript", {
                    "type": "transcript",
                    "full_text": transcript_data.get("full_text", ""),
                    "language": "en",
                    "turns": transcript_data.get("transcript_turns", []),
                })

                # Add call analysis if available
                if transcript_data.get("analysis"):
                    analysis_info = transcript_data["analysis"]
                    add("summary", {
                        "type": "summary",
                        "summary": analysis_info.get("summary"),
                        "title": analysis_info.get("title"),
                        "call_successful": analysis_info.get("call_successful"),
                    })

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

                add("transcript", analysis_data)

                logger.debug("Added simple transcript to vCon")

        except Exception as e:
            logger.error(f"Error adding analysis: {str(e)}")

    def _add_tags(self, vcon: Vcon, conversation: Conversation):
        """Add tags to vCon"""
        try:
            if not vcon.parties:
                # A tags attachment needs the party that adds it.
                logger.debug("No parties; skipping tags")
                return

            # vcon-lib writes the tags attachment with party 0 and every
            # Session as its scope.
            vcon.add_tag("source", "elevenlabs")
            vcon.add_tag("conversation_id", conversation.id)
            vcon.add_tag("agent_id", conversation.agent_id)
            vcon.add_tag("status", conversation.status)

            for tag in conversation.tags:
                vcon.add_tag("user_tag", tag)

            logger.debug("Added tags to vCon")

        except Exception as e:
            logger.error(f"Error adding tags: {str(e)}")
