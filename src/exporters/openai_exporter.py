"""
OpenAI Files API Exporter

Exports vCon objects to OpenAI's Files API for use with assistants,
retrieval augmented generation (RAG), and other AI features.
"""

import json
import logging
from typing import Optional
import os

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None


class OpenAIExporter:
    """Export vCons to OpenAI Files API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        purpose: str = "assistants",
    ):
        """
        Initialize OpenAI exporter.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            organization: OpenAI organization ID (optional)
            purpose: Purpose of file upload ('assistants', 'batch', 'fine-tune', 'vision')
        """
        if OpenAI is None:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.organization = organization or os.getenv("OPENAI_ORG_ID")
        self.purpose = purpose
        self.logger = logging.getLogger(__name__)

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key, organization=self.organization)

    def export(self, vcon) -> dict:
        """
        Export vCon to OpenAI Files API.

        Args:
            vcon: Vcon object to export

        Returns:
            Dictionary with file info: {file_id, filename, size, purpose, status}

        Raises:
            Exception: If upload fails
        """
        try:
            # Convert vCon to JSON
            vcon_json = self._prepare_vcon(vcon)

            # Create temporary file
            filename = f"vcon_{vcon.uuid}.json"
            file_path = f"/tmp/{filename}"

            with open(file_path, "w") as f:
                json.dump(vcon_json, f, indent=2, default=str)

            # Upload to OpenAI Files API
            file_size = os.path.getsize(file_path)
            
            with open(file_path, "rb") as f:
                response = self.client.files.create(
                    file=f, purpose=self.purpose
                )

            # Clean up temp file
            os.remove(file_path)

            self.logger.info(f"Uploaded vCon to OpenAI: {response.id}")

            return {
                "file_id": response.id,
                "filename": response.filename,
                "size": file_size,
                "purpose": self.purpose,
                "status": "uploaded",
            }

        except Exception as e:
            self.logger.error(f"Failed to upload vCon to OpenAI: {e}")
            raise

    def _prepare_vcon(self, vcon) -> dict:
        """Prepare vCon for OpenAI upload."""
        if isinstance(vcon, dict):
            return vcon
        elif hasattr(vcon, "to_dict"):
            # vcon.Vcon
            return vcon.to_dict()
        elif hasattr(vcon, "dict"):
            return vcon.dict()
        elif hasattr(vcon, "__dict__"):
            return {
                "uuid": str(getattr(vcon, "uuid", "")),
                "parties": getattr(vcon, "parties", []),
                "dialog": getattr(vcon, "dialog", []),
                "analysis": getattr(vcon, "analysis", []),
                "attachments": getattr(vcon, "attachments", []),
            }
        return vcon

    def list_files(self, purpose: Optional[str] = None) -> list:
        """
        List uploaded files in OpenAI.

        Args:
            purpose: Filter by purpose (optional)

        Returns:
            List of file objects
        """
        try:
            files = self.client.files.list()
            if purpose:
                files = [f for f in files if f.purpose == purpose]
            return list(files)
        except Exception as e:
            self.logger.error(f"Failed to list OpenAI files: {e}")
            raise

    def delete_file(self, file_id: str) -> bool:
        """
        Delete file from OpenAI.

        Args:
            file_id: OpenAI file ID to delete

        Returns:
            True if successful
        """
        try:
            self.client.files.delete(file_id)
            self.logger.info(f"Deleted OpenAI file: {file_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete OpenAI file: {e}")
            raise

    def retrieve_file(self, file_id: str) -> dict:
        """
        Retrieve file metadata from OpenAI.

        Args:
            file_id: OpenAI file ID

        Returns:
            File metadata
        """
        try:
            file_obj = self.client.files.retrieve(file_id)
            
            # Extract size safely
            file_size = None
            if hasattr(file_obj, "size_bytes") and file_obj.size_bytes:
                file_size = file_obj.size_bytes
            
            return {
                "file_id": file_obj.id,
                "filename": file_obj.filename,
                "size": file_size,
                "purpose": file_obj.purpose,
                "created_at": file_obj.created_at,
            }
        except Exception as e:
            self.logger.error(f"Failed to retrieve OpenAI file: {e}")
            raise

    def export_batch(self, vcons: list) -> list:
        """
        Export multiple vCons to OpenAI.

        Args:
            vcons: List of Vcon objects

        Returns:
            List of file info dictionaries
        """
        results = []
        for vcon in vcons:
            try:
                result = self.export(vcon)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to export vCon: {e}")
                results.append({"error": str(e)})
        return results
