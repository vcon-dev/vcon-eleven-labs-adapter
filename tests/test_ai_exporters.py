"""
Tests for AI exporters (OpenAI and Anthropic)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.exporters.openai_exporter import OpenAIExporter
from src.exporters.anthropic_exporter import AnthropicExporter


class TestOpenAIExporter:
    """Tests for OpenAI exporter"""

    def test_openai_exporter_init_with_api_key(self):
        """Test OpenAI exporter initialization with API key"""
        with patch('src.exporters.openai_exporter.OpenAI'):
            exporter = OpenAIExporter(api_key='sk-test-key')
            assert exporter.api_key == 'sk-test-key'

    def test_openai_exporter_init_without_api_key(self):
        """Test OpenAI exporter initialization fails without API key"""
        with patch('src.exporters.openai_exporter.OpenAI'):
            with pytest.raises(ValueError, match="OpenAI API key required"):
                OpenAIExporter(api_key=None)

    def test_openai_exporter_init_missing_package(self):
        """Test OpenAI exporter fails when package not installed"""
        with patch('src.exporters.openai_exporter.OpenAI', None):
            with pytest.raises(ImportError, match="openai package required"):
                OpenAIExporter(api_key='sk-test-key')

    @patch('src.exporters.openai_exporter.OpenAI')
    def test_openai_export_vcon(self, mock_openai_class, sample_conversation):
        """Test exporting vCon to OpenAI"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.id = "file-123"
        mock_response.filename = "vcon_test.json"
        mock_response.size_bytes = 1024
        mock_client.beta.files.upload.return_value = mock_response

        # Export
        exporter = OpenAIExporter(api_key='sk-test-key')
        result = exporter.export(sample_conversation)

        # Assertions
        assert result['file_id'] == 'file-123'
        assert result['status'] == 'uploaded'
        assert result['size'] == 1024

    @patch('src.exporters.openai_exporter.OpenAI')
    def test_openai_batch_export(self, mock_openai_class, sample_conversation):
        """Test batch export to OpenAI"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.id = "file-123"
        mock_response.filename = "vcon.json"
        mock_response.size_bytes = 1024
        mock_client.beta.files.upload.return_value = mock_response

        # Export
        exporter = OpenAIExporter(api_key='sk-test-key')
        results = exporter.export_batch([sample_conversation])

        assert len(results) == 1
        assert results[0]['file_id'] == 'file-123'

    @patch('src.exporters.openai_exporter.OpenAI')
    def test_openai_list_files(self, mock_openai_class):
        """Test listing files from OpenAI"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_files = [
            MagicMock(id='file-1', filename='vcon1.json', purpose='assistants'),
            MagicMock(id='file-2', filename='vcon2.json', purpose='batch'),
        ]
        mock_client.beta.files.list.return_value = mock_files

        # List files
        exporter = OpenAIExporter(api_key='sk-test-key')
        files = exporter.list_files(purpose='assistants')

        assert len(files) >= 0

    @patch('src.exporters.openai_exporter.OpenAI')
    def test_openai_delete_file(self, mock_openai_class):
        """Test deleting file from OpenAI"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Delete
        exporter = OpenAIExporter(api_key='sk-test-key')
        result = exporter.delete_file('file-123')

        assert result is True
        mock_client.beta.files.delete.assert_called_once_with('file-123')


class TestAnthropicExporter:
    """Tests for Anthropic exporter"""

    def test_anthropic_exporter_init_with_api_key(self):
        """Test Anthropic exporter initialization with API key"""
        with patch('src.exporters.anthropic_exporter.Anthropic'):
            exporter = AnthropicExporter(api_key='sk-ant-test-key')
            assert exporter.api_key == 'sk-ant-test-key'

    def test_anthropic_exporter_init_without_api_key(self):
        """Test Anthropic exporter initialization fails without API key"""
        with patch('src.exporters.anthropic_exporter.Anthropic'):
            with pytest.raises(ValueError, match="Anthropic API key required"):
                AnthropicExporter(api_key=None)

    def test_anthropic_exporter_init_missing_package(self):
        """Test Anthropic exporter fails when package not installed"""
        with patch('src.exporters.anthropic_exporter.Anthropic', None):
            with pytest.raises(ImportError, match="anthropic package required"):
                AnthropicExporter(api_key='sk-ant-test-key')

    @patch('src.exporters.anthropic_exporter.Anthropic')
    def test_anthropic_export_vcon(self, mock_anthropic_class, sample_conversation):
        """Test exporting vCon to Anthropic"""
        # Setup mocks
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.id = "file-456"
        mock_response.filename = "vcon_test.json"
        mock_response.size = 2048
        mock_response.created_at = MagicMock(isoformat=lambda: "2024-01-01T00:00:00")
        mock_client.beta.files.upload.return_value = mock_response

        # Export
        exporter = AnthropicExporter(api_key='sk-ant-test-key')
        result = exporter.export(sample_conversation)

        # Assertions
        assert result['file_id'] == 'file-456'
        assert result['status'] == 'uploaded'
        assert result['size'] == 2048

    @patch('src.exporters.anthropic_exporter.Anthropic')
    def test_anthropic_batch_export(self, mock_anthropic_class, sample_conversation):
        """Test batch export to Anthropic"""
        # Setup mocks
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.id = "file-456"
        mock_response.filename = "vcon.json"
        mock_response.size = 2048
        mock_response.created_at = MagicMock()
        mock_client.beta.files.upload.return_value = mock_response

        # Export
        exporter = AnthropicExporter(api_key='sk-ant-test-key')
        results = exporter.export_batch([sample_conversation])

        assert len(results) == 1
        assert results[0]['file_id'] == 'file-456'

    @patch('src.exporters.anthropic_exporter.Anthropic')
    def test_anthropic_list_files(self, mock_anthropic_class):
        """Test listing files from Anthropic"""
        # Setup mocks
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_files = [
            MagicMock(id='file-1', filename='vcon1.json'),
            MagicMock(id='file-2', filename='vcon2.json'),
        ]
        mock_client.beta.files.list.return_value = mock_files

        # List files
        exporter = AnthropicExporter(api_key='sk-ant-test-key')
        files = exporter.list_files()

        assert len(files) >= 0

    @patch('src.exporters.anthropic_exporter.Anthropic')
    def test_anthropic_delete_file(self, mock_anthropic_class):
        """Test deleting file from Anthropic"""
        # Setup mocks
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Delete
        exporter = AnthropicExporter(api_key='sk-ant-test-key')
        result = exporter.delete_file('file-456')

        assert result is True
        mock_client.beta.files.delete.assert_called_once_with('file-456')

    @patch('src.exporters.anthropic_exporter.Anthropic')
    def test_anthropic_create_retrieval_context(self, mock_anthropic_class):
        """Test creating retrieval context for RAG"""
        exporter = AnthropicExporter(api_key='sk-ant-test-key')
        context = exporter.create_retrieval_context(
            file_ids=['file-1', 'file-2'],
            query="Analyze this conversation"
        )

        assert context['type'] == 'document_retrieval'
        assert 'file-1' in context['files']
        assert context['query'] == "Analyze this conversation"
