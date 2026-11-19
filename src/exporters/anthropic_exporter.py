"""
Anthropic Files API Exporter

Exports vCon objects to Anthropic's Files API for use with Claude,
retrieval augmented generation (RAG), and other AI features.
"""

import json
import logging
from typing import Optional
import os

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None
    Anthropic = None


class AnthropicExporter:
    """Export vCons to Anthropic Files API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Anthropic exporter.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            timeout: Request timeout in seconds
        """
        if Anthropic is None:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required")

        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key, timeout=timeout)

    def export(self, vcon) -> dict:
        """
        Export vCon to Anthropic Files API.

        Args:
            vcon: Vcon object to export

        Returns:
            Dictionary with file info: {file_id, size, status, created_at}

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

            # Upload to Anthropic Files API
            file_size = os.path.getsize(file_path)

            with open(file_path, "rb") as f:
                response = self.client.beta.files.upload(
                    file=(filename, f, "application/json"),
                )

            # Clean up temp file
            os.remove(file_path)

            self.logger.info(f"Uploaded vCon to Anthropic: {response.id}")

            # Extract size safely - use calculated file_size if response doesn't have it
            response_size = file_size
            if hasattr(response, "size") and response.size:
                response_size = response.size
            elif hasattr(response, "size_bytes") and response.size_bytes:
                response_size = response.size_bytes

            return {
                "file_id": response.id,
                "filename": response.filename,
                "size": response_size,
                "status": "uploaded",
                "created_at": response.created_at.isoformat()
                if hasattr(response, "created_at")
                else None,
            }

        except Exception as e:
            self.logger.error(f"Failed to upload vCon to Anthropic: {e}")
            raise

    def _prepare_vcon(self, vcon) -> dict:
        """Prepare vCon for Anthropic upload."""
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

    def list_files(self, limit: int = 100) -> list:
        """
        List uploaded files in Anthropic.

        Args:
            limit: Maximum number of files to return

        Returns:
            List of file objects
        """
        try:
            files = self.client.beta.files.list(limit=limit)
            return list(files)
        except Exception as e:
            self.logger.error(f"Failed to list Anthropic files: {e}")
            raise

    def delete_file(self, file_id: str) -> bool:
        """
        Delete file from Anthropic.

        Args:
            file_id: Anthropic file ID to delete

        Returns:
            True if successful
        """
        try:
            self.client.beta.files.delete(file_id)
            self.logger.info(f"Deleted Anthropic file: {file_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete Anthropic file: {e}")
            raise

    def retrieve_file(self, file_id: str) -> dict:
        """
        Retrieve file metadata from Anthropic.

        Args:
            file_id: Anthropic file ID

        Returns:
            File metadata
        """
        try:
            file_obj = self.client.beta.files.retrieve(file_id)
            
            # Extract size safely
            file_size = None
            if hasattr(file_obj, "size") and file_obj.size:
                file_size = file_obj.size
            elif hasattr(file_obj, "size_bytes") and file_obj.size_bytes:
                file_size = file_obj.size_bytes
            
            return {
                "file_id": file_obj.id,
                "filename": file_obj.filename,
                "size": file_size,
                "created_at": file_obj.created_at.isoformat()
                if hasattr(file_obj, "created_at")
                else None,
            }
        except Exception as e:
            self.logger.error(f"Failed to retrieve Anthropic file: {e}")
            raise

    def export_batch(self, vcons: list) -> list:
        """
        Export multiple vCons to Anthropic.

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

    def create_retrieval_context(
        self, file_ids: list, query: str
    ) -> dict:
        """
        Create a retrieval context for RAG with Claude.

        Args:
            file_ids: List of Anthropic file IDs
            query: User query or context

        Returns:
            Retrieval context for passing to Claude
        """
        return {
            "type": "document_retrieval",
            "files": file_ids,
            "query": query,
        }
