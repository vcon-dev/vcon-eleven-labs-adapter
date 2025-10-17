# Testing Guide

Complete guide to testing the vCon ElevenLabs Adapter.

## Overview

The adapter includes a comprehensive test suite with:
- 130+ unit and integration tests
- 90%+ code coverage
- Full pytest integration
- Comprehensive fixtures
- Mock testing for external services

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_models.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_models.py::TestConversation -v
```

### Run Specific Test

```bash
pytest tests/test_models.py::TestConversation::test_create_conversation -v
```

## Coverage Report

### Generate Coverage Report

```bash
pytest --cov=src --cov-report=term-missing
```

### Generate HTML Coverage Report

```bash
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

### Set Minimum Coverage Threshold

```bash
pytest --cov=src --cov-fail-under=80
```

## Test Structure

### Test Files

```
tests/
├── __init__.py
├── conftest.py              # Fixtures and configuration
├── test_models.py           # 50+ model tests
├── test_extractors.py       # 25+ extractor tests
├── test_transformers.py     # 25+ transformer tests
├── test_exporters.py        # 30+ exporter tests
└── pytest.ini               # Pytest configuration
```

### Test Statistics

| Component | Tests | Coverage |
|-----------|-------|----------|
| Models | 50+ | 95%+ |
| Extractors | 25+ | 90%+ |
| Transformers | 25+ | 85%+ |
| Exporters | 30+ | 90%+ |
| **Total** | **130+** | **90%+** |

## Test Fixtures

### Data Fixtures

Available fixtures in `tests/conftest.py`:

- `sample_agent`: Complete Agent object
- `sample_participants`: List of participants
- `sample_audio_recording`: AudioRecording object
- `sample_transcript`: Transcript object
- `sample_conversation`: Full Conversation object
- `sample_conversation_no_audio`: Conversation without audio

### Mock Fixtures

- `mock_elevenlabs_client`: Mocked ElevenLabs API
- `mock_s3_client`: Mocked AWS S3
- `mock_requests_post`: Mocked HTTP requests

### Using Fixtures

```python
def test_something(sample_conversation):
    """Test using sample conversation fixture"""
    assert sample_conversation.id == "conv_123"
    assert len(sample_conversation.participants) == 2
```

## Test Categories

### 1. Model Tests (test_models.py)

Tests for all Pydantic data models:

```bash
pytest tests/test_models.py
```

**Covers:**
- Model creation
- Default values
- Optional fields
- Validation errors
- Serialization

### 2. Extractor Tests (test_extractors.py)

Tests for ElevenLabs API client:

```bash
pytest tests/test_extractors.py
```

**Covers:**
- Initialization
- Agent listing
- Conversation retrieval
- Audio fetching
- Retry logic
- Error handling

### 3. Transformer Tests (test_transformers.py)

Tests for vCon transformation:

```bash
pytest tests/test_transformers.py
```

**Covers:**
- Party mapping
- Dialog processing
- vCon building
- Metadata management
- Validation

### 4. Exporter Tests (test_exporters.py)

Tests for export backends:

```bash
pytest tests/test_exporters.py
```

**Covers:**
- File export
- S3 export
- Webhook export
- Batch operations
- Error handling

## Writing New Tests

### Test Template

```python
"""
Tests for a new component
"""

import pytest
from src.components.my_module import MyClass


class TestMyClass:
    """Tests for MyClass"""

    def test_something(self, sample_conversation):
        """Test a specific behavior"""
        # Arrange
        instance = MyClass()
        
        # Act
        result = instance.do_something(sample_conversation)
        
        # Assert
        assert result is not None
        assert isinstance(result, ExpectedType)
```

### Best Practices

1. **Use Fixtures**: Leverage fixtures for common data
2. **Clear Names**: Use descriptive test names
3. **Arrange-Act-Assert**: Follow the AAA pattern
4. **One Assertion Per Test**: Keep tests focused
5. **Mock External Services**: Don't call real APIs
6. **Test Error Cases**: Test both success and failure
7. **Document Complex Tests**: Add docstrings

### Example: Adding a Test

```python
def test_vcon_builder_with_audio(self, sample_conversation):
    """Test that vCon builder includes audio correctly"""
    # Arrange
    builder = VconBuilder()
    expected_audio_type = "audio"
    
    # Act
    vcon = builder.build_vcon(sample_conversation)
    dialogs = vcon.dialog
    
    # Assert
    assert dialogs is not None
    assert len(dialogs) > 0
    assert any(d.get('type') == expected_audio_type for d in dialogs)
```

## Mocking External Services

### Mock ElevenLabs API

```python
from unittest.mock import patch, MagicMock

@patch("src.extractors.elevenlabs_extractor.ElevenLabs")
def test_with_mock_api(mock_elevenlabs_class):
    mock_client = MagicMock()
    mock_elevenlabs_class.return_value = mock_client
    
    # Test code here
```

### Mock S3

```python
from unittest.mock import patch

@patch("src.exporters.s3_exporter.boto3.client")
def test_s3_export(mock_boto3):
    mock_s3 = MagicMock()
    mock_boto3.return_value = mock_s3
    
    # Test code here
```

### Mock Webhooks

```python
from unittest.mock import patch

@patch("src.exporters.webhook_exporter.requests.post")
def test_webhook_export(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    
    # Test code here
```

## Advanced Testing

### Run Tests in Parallel

```bash
pip install pytest-xdist
pytest -n auto
```

### Performance Testing

```bash
# Show slowest 10 tests
pytest --durations=10
```

### Test with Coverage

```bash
pytest --cov=src --cov-report=html --cov-fail-under=80
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting Tests

### Tests Not Found

```bash
# Verify pytest can find tests
pytest --collect-only

# Check file naming (must be test_*.py or *_test.py)
```

### Import Errors

```bash
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest

# Or install in development mode
pip install -e .
```

### Fixture Not Found

```bash
# Ensure conftest.py is in tests/ directory
ls tests/conftest.py

# List all available fixtures
pytest --fixtures
```

### Module Not Found When Running Tests

```bash
# Install package in development mode
pip install -e .

# Then run tests
pytest
```

## Running Specific Test Scenarios

### Test Only Models

```bash
pytest tests/test_models.py
```

### Test Only Extractors

```bash
pytest tests/test_extractors.py
```

### Test Only Transformers

```bash
pytest tests/test_transformers.py
```

### Test Only Exporters

```bash
pytest tests/test_exporters.py
```

### Test with Print Statements

```bash
# Show print output
pytest -s
```

### Drop into Debugger

```python
def test_something():
    import pdb; pdb.set_trace()
    # Test code here
```

## Test Maintenance

### When to Update Tests

- When code changes
- When adding new features
- When fixing bugs

### Regular Tasks

- Run full test suite weekly
- Update fixtures as models evolve
- Review coverage reports
- Keep dependencies up to date
- Monitor test execution time

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Unittest Mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

For more information:
- [User Guide](../02-usage/user-guide.md)
- [Live Testing](live-testing.md)
- [Debugging Guide](scenarios.md)
