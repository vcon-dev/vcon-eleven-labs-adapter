# Contributing to vCon ElevenLabs Adapter

Thank you for your interest in contributing to the vCon ElevenLabs Adapter! We welcome contributions from the community.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/vcon-eleven-labs-adapter.git
   cd vcon-eleven-labs-adapter
   ```

3. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set up development environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

## Development Workflow

### Code Changes

1. **Make your changes** in a descriptive branch
2. **Write tests** for new features:
   ```bash
   pytest tests/
   ```

3. **Check coverage**:
   ```bash
   pytest --cov=src --cov-report=html
   ```

4. **Verify code quality**:
   - Use type hints
   - Add docstrings
   - Follow PEP 8 style
   - Keep tests passing

### Commit Messages

Use clear, descriptive commit messages:

```
[FEATURE] Add new exporter for database backend
[FIX] Resolve timeout issue in API client
[DOCS] Update configuration reference
[TEST] Add tests for party mapper
```

Format: `[TYPE] Description`

Types: FEATURE, FIX, DOCS, TEST, REFACTOR, PERF

### Documentation

1. **Update docs/** if adding features:
   ```bash
   # Edit relevant documentation files
   docs/02-usage/user-guide.md
   docs/02-usage/api-reference.md
   ```

2. **Add code examples** if needed:
   ```bash
   # Add to docs/02-usage/examples.md
   ```

3. **Update README** if major changes:
   ```bash
   vim README.md
   ```

## Pull Request Process

1. **Test locally**:
   ```bash
   pytest tests/ -v
   pytest --cov=src --cov-fail-under=80
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request** on GitHub:
   - Clear title and description
   - Reference any related issues
   - Include testing information
   - Mention breaking changes if any

4. **Respond to feedback**:
   - Address code review comments
   - Push additional commits as needed
   - Re-run tests for each change

## Code Style

### Python Code

- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for all public methods
- **Max line length**: 100 characters

Example:
```python
def process_conversation(
    self,
    conversation: Conversation,
    agent_id: str
) -> Vcon:
    """
    Process a conversation into vCon format.

    Args:
        conversation: Conversation object to process
        agent_id: ID of the agent

    Returns:
        Processed Vcon object

    Raises:
        ValueError: If conversation is invalid
    """
    # Implementation here
    pass
```

### Test Code

- **Pytest** framework
- **Fixtures** for common data
- **Mocks** for external services
- **Descriptive names** for test functions
- **Arrange-Act-Assert** pattern

Example:
```python
def test_vcon_builder_with_audio(sample_conversation):
    """Test that vCon builder includes audio correctly."""
    # Arrange
    builder = VconBuilder()
    
    # Act
    vcon = builder.build_vcon(sample_conversation)
    
    # Assert
    assert vcon is not None
    assert vcon.uuid is not None
    assert len(vcon.dialog) > 0
```

## Areas for Contribution

### Code

- [ ] New exporters (database, FTP, SFTP, etc.)
- [ ] Async/await support
- [ ] Performance optimizations
- [ ] Bug fixes
- [ ] Error handling improvements

### Documentation

- [ ] Usage examples
- [ ] Tutorial improvements
- [ ] API documentation
- [ ] Deployment guides
- [ ] Configuration examples

### Testing

- [ ] Additional test coverage
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge case scenarios

### Community

- [ ] Issue reporting
- [ ] Bug fixes
- [ ] Feature requests
- [ ] Documentation updates

## Testing Requirements

All contributions must include:

- [x] Tests for new features
- [x] All existing tests passing
- [x] 80%+ coverage for new code
- [x] No breaking changes (document if unavoidable)

Run tests before submitting:
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific component
pytest tests/test_models.py -v
```

## Documentation Standards

- [ ] Code comments for complex logic
- [ ] Docstrings following Google style
- [ ] README updates if user-facing
- [ ] Examples for new features
- [ ] API docs if adding methods

## Reporting Issues

### Bug Reports

Include:
- Python version
- Operating system
- Error message and traceback
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests

Include:
- Use case/problem statement
- Proposed solution
- Alternative approaches
- Examples if applicable

## Code Review Process

Reviewers will check for:

1. **Functionality**
   - Does it work as intended?
   - Are edge cases handled?
   - Is error handling appropriate?

2. **Code Quality**
   - Type hints present?
   - Docstrings complete?
   - PEP 8 compliant?
   - Tests included?

3. **Testing**
   - Adequate coverage?
   - All tests passing?
   - Edge cases covered?

4. **Documentation**
   - User guide updated?
   - API docs updated?
   - Examples provided?

## Questions or Need Help?

- Check the [Documentation](docs/README.md)
- Review [FAQ](docs/03-testing/scenarios.md)
- Look at existing issues
- Check discussions

## License

By contributing, you agree your contributions will be licensed under the MIT License.

## Acknowledgments

Contributors will be recognized in:
- Project README
- Release notes
- Contributors file

Thank you for contributing!

---

**Need help?** Open an issue or check the documentation.
