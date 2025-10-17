"""
Tests for vCon exporters
"""

import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.exporters.file_exporter import FileExporter
from src.exporters.s3_exporter import S3Exporter
from src.exporters.webhook_exporter import WebhookExporter
from src.transformers.vcon_builder import VconBuilder


class TestFileExporter:
    """Tests for FileExporter"""

    def test_initialization(self, tmp_path):
        """Test FileExporter initialization"""
        exporter = FileExporter(directory=str(tmp_path))

        assert exporter.directory == tmp_path

    def test_export_creates_file(self, tmp_path, sample_conversation):
        """Test that export creates a file"""
        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = FileExporter(directory=str(tmp_path))
        path = exporter.export(vcon)

        assert path.exists()
        assert path.suffix == ".json"

    def test_export_contains_valid_json(self, tmp_path, sample_conversation):
        """Test that exported file contains valid JSON"""
        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = FileExporter(directory=str(tmp_path))
        path = exporter.export(vcon)

        with open(path, "r") as f:
            data = json.load(f)

        assert "uuid" in data or "vcon" in data

    def test_export_custom_filename(self, tmp_path, sample_conversation):
        """Test exporting with custom filename"""
        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = FileExporter(directory=str(tmp_path))
        path = exporter.export(vcon, filename="custom_name.json")

        assert path.name == "custom_name.json"
        assert path.exists()

    def test_export_no_overwrite(self, tmp_path, sample_conversation):
        """Test that existing files are not overwritten by default"""
        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = FileExporter(directory=str(tmp_path), overwrite=False)

        path1 = exporter.export(vcon, filename="test.json")
        assert path1.exists()

        original_size = path1.stat().st_size

        vcon2 = builder.build_vcon(sample_conversation)
        path2 = exporter.export(vcon2, filename="test.json")

        assert path2.stat().st_size == original_size

    def test_export_batch(self, tmp_path, sample_conversation):
        """Test batch export"""
        builder = VconBuilder()
        vcons = [
            builder.build_vcon(sample_conversation),
            builder.build_vcon(sample_conversation),
        ]

        exporter = FileExporter(directory=str(tmp_path))
        paths = exporter.export_batch(vcons)

        assert len(paths) == 2
        assert all(p.exists() for p in paths)


class TestS3Exporter:
    """Tests for S3Exporter"""

    @patch("src.exporters.s3_exporter.boto3.client")
    def test_initialization(self, mock_boto3):
        """Test S3Exporter initialization"""
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3

        exporter = S3Exporter(bucket="test-bucket")

        assert exporter.bucket == "test-bucket"
        assert exporter.region == "us-east-1"
        assert exporter.prefix == "elevenlabs/"

    @patch("src.exporters.s3_exporter.boto3.client")
    def test_export_uploads_to_s3(self, mock_boto3, sample_conversation):
        """Test that export uploads to S3"""
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3

        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = S3Exporter(bucket="test-bucket")
        key = exporter.export(vcon)

        mock_s3.put_object.assert_called_once()
        assert "elevenlabs/" in key

    @patch("src.exporters.s3_exporter.boto3.client")
    def test_export_with_custom_key(self, mock_boto3, sample_conversation):
        """Test export with custom S3 key"""
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3

        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = S3Exporter(bucket="test-bucket")
        key = exporter.export(vcon, key="custom_key.json")

        assert "custom_key.json" in key

    @patch("src.exporters.s3_exporter.boto3.client")
    def test_export_with_encryption(self, mock_boto3, sample_conversation):
        """Test export with encryption"""
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3

        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = S3Exporter(
            bucket="test-bucket",
            encryption="AES256",
        )
        key = exporter.export(vcon)

        call_kwargs = mock_s3.put_object.call_args[1]
        assert call_kwargs.get("ServerSideEncryption") == "AES256"

    @patch("src.exporters.s3_exporter.boto3.client")
    def test_verify_bucket_access(self, mock_boto3):
        """Test bucket access verification"""
        mock_s3 = MagicMock()
        mock_s3.head_bucket.return_value = {}
        mock_boto3.return_value = mock_s3

        exporter = S3Exporter(bucket="test-bucket")
        result = exporter.verify_bucket_access()

        assert result is True
        mock_s3.head_bucket.assert_called_once()

    @patch("src.exporters.s3_exporter.boto3.client")
    def test_verify_bucket_access_failure(self, mock_boto3):
        """Test bucket access verification failure"""
        mock_s3 = MagicMock()
        mock_s3.head_bucket.side_effect = Exception("Access Denied")
        mock_boto3.return_value = mock_s3

        exporter = S3Exporter(bucket="test-bucket")
        result = exporter.verify_bucket_access()

        assert result is False


class TestWebhookExporter:
    """Tests for WebhookExporter"""

    def test_initialization(self):
        """Test WebhookExporter initialization"""
        exporter = WebhookExporter(url="https://example.com/webhook")

        assert exporter.url == "https://example.com/webhook"
        assert exporter.retry_attempts == 3

    @patch("src.exporters.webhook_exporter.requests.post")
    def test_export_posts_to_webhook(self, mock_post, sample_conversation):
        """Test that export POSTs to webhook"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = WebhookExporter(url="https://example.com/webhook")
        result = exporter.export(vcon)

        assert result is True
        mock_post.assert_called_once()

    @patch("src.exporters.webhook_exporter.requests.post")
    def test_export_webhook_error(self, mock_post, sample_conversation):
        """Test handling webhook error"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = WebhookExporter(url="https://example.com/webhook", retry_attempts=1)
        result = exporter.export(vcon)

        assert result is False

    @patch("src.exporters.webhook_exporter.requests.post")
    def test_export_with_bearer_auth(self, mock_post, sample_conversation):
        """Test export with Bearer authentication"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = WebhookExporter(
            url="https://example.com/webhook",
            api_key="test_token",
            auth_type="bearer",
        )
        result = exporter.export(vcon)

        assert result is True

        call_kwargs = mock_post.call_args[1]
        assert "Authorization" in call_kwargs["headers"]
        assert "Bearer test_token" in call_kwargs["headers"]["Authorization"]

    @patch("src.exporters.webhook_exporter.requests.post")
    def test_export_batch(self, mock_post, sample_conversation):
        """Test batch export to webhook"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        builder = VconBuilder()
        vcons = [
            builder.build_vcon(sample_conversation),
            builder.build_vcon(sample_conversation),
        ]

        exporter = WebhookExporter(url="https://example.com/webhook")
        results = exporter.export_batch(vcons, batch_size=1)

        assert results["total"] == 2
        assert results["successful"] == 2

    @patch("src.exporters.webhook_exporter.requests.post")
    def test_verify_webhook(self, mock_post):
        """Test webhook verification"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        exporter = WebhookExporter(url="https://example.com/webhook")
        result = exporter.verify_webhook()

        assert result is True

    @patch("src.exporters.webhook_exporter.requests.post")
    def test_verify_webhook_failure(self, mock_post):
        """Test webhook verification failure"""
        mock_post.side_effect = Exception("Connection error")

        exporter = WebhookExporter(url="https://example.com/webhook")
        result = exporter.verify_webhook()

        assert result is False


class TestExporterIntegration:
    """Integration tests for exporters"""

    def test_file_exporter_with_vcon(self, tmp_path, sample_conversation):
        """Test complete file export workflow"""
        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = FileExporter(directory=str(tmp_path))
        path = exporter.export(vcon)

        assert path.exists()
        assert path.stat().st_size > 0

        with open(path, "r") as f:
            data = json.load(f)
            assert data is not None

    @patch("src.exporters.s3_exporter.boto3.client")
    def test_s3_exporter_with_vcon(self, mock_boto3, sample_conversation):
        """Test complete S3 export workflow"""
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3

        builder = VconBuilder()
        vcon = builder.build_vcon(sample_conversation)

        exporter = S3Exporter(bucket="test-bucket")
        key = exporter.export(vcon)

        assert key is not None
        mock_s3.put_object.assert_called()
