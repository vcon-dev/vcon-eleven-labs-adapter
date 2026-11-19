"""
Processes conversation dialog data into vCon Dialog objects (vCon core-05).

Dialog `parties` are the contributors to that Dialog. An ElevenLabs
conversation is a two-way exchange, so the recording and the transcript list
every participant; the receivers are on the Session that `VconBuilder` adds.
"""

import base64
import hashlib
from typing import List, Optional
from vcon.dialog import Dialog
from src.models.elevenlabs_models import Conversation
from src.logger import get_logger

logger = get_logger(__name__)

# ElevenLabs audio formats to registered media types.
AUDIO_MEDIATYPES = {
    "mp3": "audio/mpeg",
    "mpeg": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "opus": "audio/opus",
    "flac": "audio/flac",
    "m4a": "audio/mp4",
    "webm": "audio/webm",
    "pcm": "audio/L16",
}


def content_hash(data: bytes) -> str:
    """Return a core-05 content_hash: `sha512-<unpadded base64url digest>`."""
    digest = base64.urlsafe_b64encode(hashlib.sha512(data).digest()).rstrip(b"=")
    return "sha512-" + digest.decode("ascii")


def audio_mediatype(fmt: Optional[str]) -> str:
    """Return the media type for an ElevenLabs audio format name."""
    fmt = (fmt or "wav").lower()
    return AUDIO_MEDIATYPES.get(fmt, f"audio/{fmt}")


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
                # No recording Dialog without media: a core-05 recording
                # Dialog carries its content inline or by URL. The Session
                # still records the conversation's start and duration.
                logger.debug(f"No audio for conversation {conversation.id}; no recording dialog")

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

            if not audio.url:
                # Without a URL (or inline bytes, see
                # create_embedded_audio_dialog) there is no content to
                # reference, so no recording Dialog.
                logger.debug("No audio URL available; no recording dialog")
                return None

            dialog_dict = {
                "type": "recording",
                "start": conversation.start_time,
                "parties": list(party_indices.values()),
                "mediatype": audio_mediatype(audio.format),
                "url": audio.url,
            }
            # core-05: a Dialog that references external content by `url`
            # carries a `content_hash` of it. Known when the adapter fetched
            # the audio itself (see ElevenLabsVconAdapter).
            if audio.content_hash:
                dialog_dict["content_hash"] = audio.content_hash
            logger.debug(f"Audio dialog with URL: {audio.url}")

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
                "mediatype": "text/plain",
                "body": transcript.text,
                "encoding": "none",
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

            # core-05 inline binary content is unpadded base64url.
            encoded_audio = base64.urlsafe_b64encode(audio_bytes).rstrip(b"=").decode("ascii")

            dialog_dict = {
                "type": "recording",
                "start": conversation.start_time,
                "parties": list(party_indices.values()),
                "mediatype": audio_mediatype(audio.format),
                "body": encoded_audio,
                "encoding": "base64url",
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
