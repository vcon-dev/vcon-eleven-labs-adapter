# Testing Guide for vCon ElevenLabs Adapter

## Overview

This document provides comprehensive information about the test suite for the vCon ElevenLabs Adapter, including how to run tests, what is tested, and how to write new tests.

## Test Structure

### Test Files

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and shared fixtures
├── test_models.py           # Data model tests (50+ tests)
├── test_extractors.py       # ElevenLabs extractor tests (25+ tests)
├── test_transformers.py     # vCon transformer tests (25+ tests)
├── test_exporters.py        # Export backend tests (30+ tests)
└── fixtures/                # Test fixture data (if needed)
```

### Test Statistics

| Component | Tests | Coverage |
|-----------|-------|----------|
| Models | 50+ | 95%+ |
| Extractors | 25+ | 90%+ |
| Transformers | 25+ | 85%+ |
| Exporters | 30+ | 90%+ |
| **Total** | **130+** | **90%+** |

## Installation

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes all testing dependencies:
- pytest
- pytest-cov
- pytest-mock

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage Report

```bash
pytest --cov=src --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

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
pytest tests/test_models.py::TestConversation::test_create_conversation_minimal -v
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests requiring external services
pytest -m external
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Detailed Output

```bash
pytest -vv
```

### Run Tests in Parallel

```bash
pip install pytest-xdist
pytest -n auto
```

## Test Coverage

### Generate Coverage Report

```bash
pytest --cov=src --cov-report=term-missing
```

### Generate HTML Coverage Report

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Minimum Coverage Threshold

```bash
pytest --cov=src --cov-fail-under=80
```

## Test Fixtures

### Available Fixtures

All fixtures are defined in `tests/conftest.py`:

#### Data Fixtures
- `sample_agent`: A complete Agent object
- `sample_participants`: List of ConversationParticipant objects
- `sample_audio_recording`: AudioRecording object
- `sample_transcript`: Transcript object
- `sample_conversation`: Complete Conversation with audio and transcript
- `sample_conversation_no_audio`: Conversation without audio

#### Mock Fixtures
- `mock_elevenlabs_client`: Mocked ElevenLabs API client
- `mock_s3_client`: Mocked AWS S3 client
- `mock_requests_post`: Mocked requests.post for webhooks

#### Configuration Fixtures
- `temp_config_file`: Temporary YAML configuration file
- `fixture_agent_dict`: Agent as dictionary
- `fixture_conversation_dict`: Conversation as dictionary

### Using Fixtures

```python
def test_something(sample_conversation):
    """Test using sample conversation fixture"""
    assert sample_conversation.id == "conv_123"
    assert len(sample_conversation.participants) == 2
```

## Test Categories

### 1. Model Tests (`test_models.py`)

Tests for all Pydantic data models:
- Conversation status enum
- Participant model
- Audio recording model
- Transcript model
- Conversation model
- Agent model
- Model validation
- Model serialization

**Run:**
```bash
pytest tests/test_models.py
```

### 2. Extractor Tests (`test_extractors.py`)

Tests for ElevenLabs API extractor:
- Initialization with various parameters
- Listing agents
- Getting conversations
- Fetching audio
- Retry logic with exponential backoff
- API error handling
- Data parsing methods
- Datetime parsing

**Run:**
```bash
pytest tests/test_extractors.py
```

### 3. Transformer Tests (`test_transformers.py`)

Tests for vCon transformation:
- Party mapping from participants
- Dialog processing from conversations
- vCon building and assembly
- Metadata and tag management
- vCon validation

**Run:**
```bash
pytest tests/test_transformers.py
```

### 4. Exporter Tests (`test_exporters.py`)

Tests for export backends:
- File exporter (filesystem export)
- S3 exporter (AWS S3 upload)
- Webhook exporter (HTTP POST)
- Batch operations
- Error handling
- Authentication and encryption
- Verification methods

**Run:**
```bash
pytest tests/test_exporters.py
```

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
        instance = MyClass()
        result = instance.do_something(sample_conversation)
        
        assert result is not None
        assert isinstance(result, ExpectedType)
```

### Best Practices

1. **Use Fixtures**: Leverage fixtures from `conftest.py` for common data
2. **Clear Names**: Use descriptive test names that explain what is tested
3. **Arrange-Act-Assert**: Follow the AAA pattern
4. **One Assertion Per Test**: Keep tests focused on a single behavior
5. **Mock External Services**: Use mocks for API calls and network requests
6. **Test Error Cases**: Test both success and failure scenarios
7. **Document Complex Tests**: Add docstrings explaining test logic

### Example: Adding a New Test

```python
def test_new_feature(self, sample_conversation):
    """Test that new feature works correctly"""
    # Arrange
    builder = VconBuilder()
    vcon = builder.build_vcon(sample_conversation)
    
    # Act
    result = new_feature_function(vcon)
    
    # Assert
    assert result is not None
    assert len(result) > 0
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
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Not Found

```bash
# Ensure pytest can find tests
pytest --collect-only

# Check test file naming
# Files must be named test_*.py or *_test.py
```

### Import Errors

```bash
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Fixture Not Found

```bash
# Ensure conftest.py is in tests/ directory
ls tests/conftest.py

# Check fixture name matches
pytest --fixtures
```

### Module Not Found When Running Tests

```bash
# Install package in development mode
pip install -e .

# Then run tests
pytest
```

## Performance Testing

### Identify Slow Tests

```bash
pytest --durations=10
```

This shows the 10 slowest tests.

### Profile Test Execution

```bash
pip install pytest-profiling
pytest --profile
```

## Test Reports

### JUnit XML Report

```bash
pytest --junit-xml=report.xml
```

### HTML Report

```bash
pip install pytest-html
pytest --html=report.html
```

## Debugging Tests

### Enable Print Statements

```bash
pytest -s
```

### Drop into Debugger

```python
def test_something():
    import pdb; pdb.set_trace()
    # Test code here
```

### Run Single Test with Verbose Output

```bash
pytest -vv -s tests/test_models.py::TestConversation::test_create_conversation_full
```

## Test Maintenance

### Update Tests When Code Changes

1. Run tests: `pytest`
2. Fix failing tests
3. Add tests for new features
4. Maintain >80% coverage

### Regular Tasks

- Run full test suite weekly
- Update fixtures as models evolve
- Review and update documentation
- Monitor test execution time
- Keep dependencies up to date

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Unittest Mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

## Contributing Tests

When contributing new tests:

1. Follow the existing test structure
2. Use appropriate fixtures
3. Include docstrings
4. Aim for >80% coverage
5. Test both success and failure cases
6. Document any new fixtures in this guide
7. Ensure all tests pass before submitting

---

**Last Updated**: October 17, 2025
**Test Framework**: pytest
**Minimum Python**: 3.8
**Target Coverage**: 90%+
