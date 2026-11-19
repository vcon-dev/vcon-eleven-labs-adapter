"""
Main ElevenLabs vCon Adapter
"""

from typing import List, Optional
from datetime import datetime

from src.config import load_config, AdapterConfig
from src.logger import setup_logger, get_logger
from src.extractors import ElevenLabsExtractor
from src.transformers import VconBuilder
from src.transformers.dialog_processor import content_hash
from src.exporters import FileExporter, S3Exporter, WebhookExporter
from src.models.elevenlabs_models import Conversation

logger = get_logger(__name__)


class ElevenLabsVconAdapter:
    """Main adapter class orchestrating the entire vCon creation pipeline"""

    def __init__(self, config_file: str):
        """
        Initialize the ElevenLabs vCon adapter

        Args:
            config_file: Path to YAML configuration file
        """
        self.config = load_config(config_file)
        self._setup_logging()

        logger.info("Initializing ElevenLabsVconAdapter")

        self.extractor = self._initialize_extractor()
        self.builder = VconBuilder(
            include_analysis=self.config.vcon.include_analysis,
            include_attachments=self.config.vcon.include_attachments,
        )
        self.exporters = self._initialize_exporters()

        logger.info("Adapter initialization complete")

    def _setup_logging(self):
        """Setup logging based on configuration"""
        setup_logger(
            name="elevenlabs_adapter",
            level=self.config.logging.level,
            log_file=self.config.logging.file,
            console=self.config.logging.console,
            format_json=(self.config.logging.format == "json"),
        )

    def _initialize_extractor(self) -> ElevenLabsExtractor:
        """Initialize ElevenLabs extractor"""
        return ElevenLabsExtractor(
            api_key=self.config.elevenlabs.api_key,
            timeout=self.config.elevenlabs.timeout,
            batch_size=self.config.elevenlabs.batch_size,
        )

    def _initialize_exporters(self) -> dict:
        """Initialize configured exporters"""
        exporters = {}

        if self.config.exporters.file.enabled:
            try:
                exporters["file"] = FileExporter(
                    directory=self.config.exporters.file.directory,
                    overwrite=self.config.exporters.file.overwrite,
                )
                logger.info("FileExporter initialized")
            except Exception as e:
                logger.error(f"Error initializing FileExporter: {str(e)}")

        if self.config.exporters.s3.enabled:
            try:
                exporters["s3"] = S3Exporter(
                    bucket=self.config.exporters.s3.bucket,
                    region=self.config.exporters.s3.region,
                    prefix=self.config.exporters.s3.prefix,
                    encryption=self.config.exporters.s3.encryption,
                )
                logger.info("S3Exporter initialized")
            except Exception as e:
                logger.error(f"Error initializing S3Exporter: {str(e)}")

        if self.config.exporters.webhook.enabled:
            try:
                exporters["webhook"] = WebhookExporter(
                    url=self.config.exporters.webhook.url,
                    api_key=self.config.exporters.webhook.api_key,
                    auth_type=self.config.exporters.webhook.auth_type,
                    retry_attempts=self.config.exporters.webhook.retry_attempts,
                )
                logger.info("WebhookExporter initialized")
            except Exception as e:
                logger.error(f"Error initializing WebhookExporter: {str(e)}")

        return exporters

    def process_all(self) -> list:
        """
        Process all configured agents

        Returns:
            List of created vCon objects
        """
        logger.info("Starting processing of all agents")

        try:
            if self.config.elevenlabs.agent_ids == "all" or self.config.elevenlabs.agent_ids == ["all"]:
                logger.info("Fetching all agents")
                agents = self.extractor.list_agents()
                agent_ids = [agent.id for agent in agents]
            else:
                agent_ids = self.config.elevenlabs.agent_ids

            vcons = []
            for agent_id in agent_ids:
                agent_vcons = self.process_agent(agent_id)
                vcons.extend(agent_vcons)

            logger.info(f"Processing complete: {len(vcons)} vCons created")
            return vcons

        except Exception as e:
            logger.error(f"Error processing all agents: {str(e)}")
            raise

    def process_agent(self, agent_id: str) -> list:
        """
        Process conversations for a specific agent

        Args:
            agent_id: ElevenLabs agent ID

        Returns:
            List of created vCon objects for this agent
        """
        logger.info(f"Processing agent: {agent_id}")

        try:
            conversations = self.extractor.get_agent_conversations(agent_id)

            if not conversations:
                logger.warning(f"No conversations found for agent {agent_id}")
                return []

            vcons = []
            for conversation in conversations:
                try:
                    vcon = self._process_conversation(conversation)
                    if vcon:
                        vcons.append(vcon)
                        self._export_vcon(vcon)

                except Exception as e:
                    logger.error(
                        f"Error processing conversation {conversation.id}: {str(e)}"
                    )

            logger.info(
                f"Successfully processed {len(vcons)} conversations for agent {agent_id}"
            )
            return vcons

        except Exception as e:
            logger.error(f"Error processing agent {agent_id}: {str(e)}")
            raise

    def process_conversation(self, conversation: Conversation):
        """
        Process a single conversation

        Args:
            conversation: Conversation object to process

        Returns:
            Created vCon object
        """
        logger.info(f"Processing conversation: {conversation.id}")

        try:
            vcon = self._process_conversation(conversation)

            if vcon:
                self._export_vcon(vcon)

            return vcon

        except Exception as e:
            logger.error(f"Error processing conversation: {str(e)}")
            raise

    def _process_conversation(self, conversation: Conversation):
        """Internal method to convert conversation to vCon"""
        try:
            # Fetch and save audio if file exporter is enabled
            audio_url = None
            if "file" in self.exporters:
                audio_bytes = self.extractor.get_conversation_audio(conversation.id)
                if audio_bytes:
                    # Save audio file
                    audio_path = self.exporters["file"].save_audio(
                        audio_bytes, conversation.id, format="mp3"
                    )
                    # Create relative URL for the vCon
                    audio_url = f"audio/{conversation.id}.mp3"
                    logger.info(f"Saved audio for conversation {conversation.id}")

                    # Update conversation audio info
                    from src.models.elevenlabs_models import AudioRecording
                    conversation.audio = AudioRecording(
                        url=audio_url,
                        duration_ms=conversation.duration_ms or 0,
                        sample_rate=16000,
                        channels=1,
                        format="mp3",
                        size_bytes=len(audio_bytes),
                        # core-05: a Dialog with `url` carries its content_hash
                        content_hash=content_hash(audio_bytes),
                    )

            # Fetch transcript
            transcript_data = self.extractor.get_conversation_transcript(conversation.id)
            if transcript_data:
                # Update conversation with transcript
                from src.models.elevenlabs_models import Transcript
                conversation.transcript = Transcript(
                    text=transcript_data.get("full_text", ""),
                    language="en",
                    confidence=None
                )

                # Store structured transcript and analysis for vCon
                conversation._transcript_data = transcript_data

            vcon = self.builder.build_vcon(conversation)
            return vcon

        except Exception as e:
            logger.error(f"Error building vCon for conversation {conversation.id}: {str(e)}")
            return None

    def _export_vcon(self, vcon):
        """Export vCon to all enabled exporters"""
        for name, exporter in self.exporters.items():
            try:
                logger.debug(f"Exporting vCon via {name}")

                if name == "file":
                    exporter.export(vcon)
                elif name == "s3":
                    exporter.export(vcon)
                elif name == "webhook":
                    exporter.export(vcon)

                logger.debug(f"Successfully exported vCon via {name}")

            except Exception as e:
                logger.error(f"Error exporting vCon via {name}: {str(e)}")

    def get_metrics(self) -> dict:
        """
        Get adapter metrics

        Returns:
            Dictionary with metrics
        """
        return {
            "exporters": list(self.exporters.keys()),
            "agent_ids": self.config.elevenlabs.agent_ids,
            "vcon_settings": {
                "include_analysis": self.config.vcon.include_analysis,
                "include_attachments": self.config.vcon.include_attachments,
            },
        }
