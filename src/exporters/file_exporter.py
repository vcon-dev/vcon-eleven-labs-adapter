"""
Exports vCons to local filesystem
"""

import json
from pathlib import Path
from typing import Optional
from vcon import Vcon
from src.logger import get_logger

logger = get_logger(__name__)


class FileExporter:
    """Exports vCons to local filesystem"""

    def __init__(self, directory: str = "./vcons", overwrite: bool = False):
        """
        Initialize file exporter

        Args:
            directory: Directory to save vCons to
            overwrite: Whether to overwrite existing files
        """
        self.directory = Path(directory)
        self.overwrite = overwrite

        self.directory.mkdir(parents=True, exist_ok=True)

        # Create audio subdirectory
        self.audio_directory = self.directory / "audio"
        self.audio_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"FileExporter initialized with directory: {self.directory}")

    def export(self, vcon: Vcon, filename: Optional[str] = None) -> Path:
        """
        Export vCon to file

        Args:
            vcon: vCon object to export
            filename: Optional custom filename (without path)

        Returns:
            Path to exported file
        """
        try:
            if filename is None:
                filename = f"{vcon.uuid}.vcon.json"

            file_path = self.directory / filename

            if file_path.exists() and not self.overwrite:
                logger.warning(
                    f"File already exists: {file_path}. Set overwrite=True to replace."
                )
                return file_path

            vcon_dict = vcon.to_dict()

            with open(file_path, "w") as f:
                json.dump(vcon_dict, f, indent=2)

            logger.info(f"Successfully exported vCon to {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error exporting vCon to file: {str(e)}")
            raise

    def save_audio(self, audio_bytes: bytes, conversation_id: str, format: str = "mp3") -> Path:
        """
        Save audio file to disk

        Args:
            audio_bytes: Audio data
            conversation_id: Conversation ID for filename
            format: Audio format extension

        Returns:
            Path to saved audio file
        """
        try:
            filename = f"{conversation_id}.{format}"
            audio_path = self.audio_directory / filename

            if audio_path.exists() and not self.overwrite:
                logger.debug(f"Audio file already exists: {audio_path}")
                return audio_path

            with open(audio_path, "wb") as f:
                f.write(audio_bytes)

            logger.info(f"Successfully saved audio to {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            raise

    def export_batch(self, vcons: list, filename_pattern: str = None) -> list:
        """
        Export multiple vCons to files

        Args:
            vcons: List of vCon objects to export
            filename_pattern: Optional pattern for filenames (e.g., "vcon_{uuid}.json")

        Returns:
            List of Path objects for exported files
        """
        paths = []

        for i, vcon in enumerate(vcons):
            try:
                if filename_pattern:
                    filename = filename_pattern.format(
                        index=i,
                        uuid=vcon.uuid,
                        agent_id=vcon.tags.get("agent_id", "unknown") if hasattr(vcon, "tags") else "unknown",
                    )
                else:
                    filename = None

                path = self.export(vcon, filename)
                paths.append(path)

            except Exception as e:
                logger.error(f"Error exporting vCon {i}: {str(e)}")

        logger.info(f"Successfully exported {len(paths)} vCons")
        return paths
