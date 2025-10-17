"""
Processes conversation dialog data into vCon Dialog objects
"""

import base64
from typing import List, Optional
from vcon.dialog import Dialog
from src.models.elevenlabs_models import Conversation
from src.logger import get_logger

logger = get_logger(__name__)


class DialogProcessor:
    """Processes conversation data into vCon Dialog entries"""

    @staticmethod
    def process_conversation_dialogs(
        conversation: Conversation,
        party_indices: dict,
        include_transcript: bool = True,
    ) -> List[Dialog]:
        """
        Convert conversation data to vCon Dialog objects

        Args:
            conversation: Conversation object with audio/transcript data
            party_indices: Dictionary mapping participant IDs to party indices
            include_transcript: Whether to include transcript as separate dialog

        Returns:
            List of Dialog objects
        """
        dialogs = []

        try:
            if conversation.audio:
                audio_dialog = DialogProcessor._create_audio_dialog(
                    conversation, party_indices
                )
                if audio_dialog:
                    dialogs.append(audio_dialog)
            else:
                # Create a placeholder recording dialog if no audio
                logger.debug(f"No audio for conversation {conversation.id}, creating placeholder dialog")
                placeholder_dialog = DialogProcessor._create_placeholder_dialog(
                    conversation, party_indices
                )
                if placeholder_dialog:
                    dialogs.append(placeholder_dialog)

            if include_transcript and conversation.transcript:
                transcript_dialog = DialogProcessor._create_transcript_dialog(
                    conversation, party_indices
                )
                if transcript_dialog:
                    dialogs.append(transcript_dialog)

            logger.info(
                f"Created {len(dialogs)} dialogs for conversation {conversation.id}"
            )
            return dialogs

        except Exception as e:
            logger.error(f"Error processing conversation dialogs: {str(e)}")
            raise

    @staticmethod
    def _create_audio_dialog(
        conversation: Conversation, party_indices: dict
    ) -> Optional[Dialog]:
        """Create a Dialog entry for audio recording"""
        try:
            audio = conversation.audio
            if not audio:
                return None

            dialog_dict = {
                "type": "recording",
                "start": conversation.start_time,
                "parties": list(party_indices.values()),
                "mimetype": f"audio/{audio.format}",
            }

            if audio.url:
                dialog_dict["url"] = audio.url
                logger.debug(f"Audio dialog with URL: {audio.url}")
            else:
                logger.debug("No audio URL available")

            if audio.duration_ms:
                dialog_dict["duration"] = audio.duration_ms / 1000

            dialog_dict["metadata"] = {
                "sample_rate": audio.sample_rate,
                "channels": audio.channels,
                "format": audio.format,
            }

            if audio.size_bytes:
                dialog_dict["metadata"]["size_bytes"] = audio.size_bytes

            dialog = Dialog(**dialog_dict)
            logger.debug(
                f"Created audio dialog for conversation {conversation.id}"
            )
            return dialog

        except Exception as e:
            logger.error(f"Error creating audio dialog: {str(e)}")
            return None

    @staticmethod
    def _create_transcript_dialog(
        conversation: Conversation, party_indices: dict
    ) -> Optional[Dialog]:
        """Create a Dialog entry for transcript"""
        try:
            transcript = conversation.transcript
            if not transcript or not transcript.text:
                return None

            dialog_dict = {
                "type": "text",
                "start": conversation.start_time,
                "parties": list(party_indices.values()),
                "mimetype": "text/plain",
                "body": transcript.text,
            }

            dialog_dict["metadata"] = {
                "language": transcript.language,
                "confidence": transcript.confidence,
                "source": "elevenlabs",
            }

            dialog = Dialog(**dialog_dict)
            logger.debug(
                f"Created transcript dialog for conversation {conversation.id}"
            )
            return dialog

        except Exception as e:
            logger.error(f"Error creating transcript dialog: {str(e)}")
            return None

    @staticmethod
    def _create_placeholder_dialog(
        conversation: Conversation, party_indices: dict
    ) -> Optional[Dialog]:
        """Create a placeholder Dialog entry for conversations without audio"""
        try:
            dialog_dict = {
                "type": "recording",
                "start": conversation.start_time,
                "parties": list(party_indices.values()),
                "mimetype": "audio/wav",
            }

            if conversation.duration_ms:
                dialog_dict["duration"] = conversation.duration_ms / 1000

            dialog_dict["metadata"] = {
                "status": conversation.status,
                "note": "Audio not available from API"
            }

            dialog = Dialog(**dialog_dict)
            logger.debug(
                f"Created placeholder dialog for conversation {conversation.id}"
            )
            return dialog

        except Exception as e:
            logger.error(f"Error creating placeholder dialog: {str(e)}")
            return None

    @staticmethod
    def create_embedded_audio_dialog(
        conversation: Conversation,
        audio_bytes: bytes,
        party_indices: dict,
    ) -> Optional[Dialog]:
        """
        Create a Dialog with embedded (base64-encoded) audio

        Args:
            conversation: Conversation object
            audio_bytes: Raw audio bytes
            party_indices: Dictionary mapping participant IDs to party indices

        Returns:
            Dialog object with embedded audio or None on error
        """
        try:
            audio = conversation.audio
            if not audio:
                return None

            encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")

            dialog_dict = {
                "type": "recording",
                "start": conversation.start_time,
                "parties": list(party_indices.values()),
                "mimetype": f"audio/{audio.format}",
                "body": encoded_audio,
                "encoding": "base64",
            }

            if audio.duration_ms:
                dialog_dict["duration"] = audio.duration_ms / 1000

            dialog = Dialog(**dialog_dict)
            logger.debug(
                f"Created embedded audio dialog for conversation {conversation.id}"
            )
            return dialog

        except Exception as e:
            logger.error(f"Error creating embedded audio dialog: {str(e)}")
            return None
