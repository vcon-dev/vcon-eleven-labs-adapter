# Installation Guide

## Prerequisites

Before installing the vCon ElevenLabs Adapter, ensure you have:

- **Python 3.8 or higher** - Check with `python --version`
- **pip** - Python package manager (usually comes with Python)
- **ElevenLabs API key** - Get it from https://elevenlabs.io/app/settings/api-keys
- **Git** (optional) - For cloning the repository
- **AWS credentials** (optional) - Only needed if using S3 export
- **Webhook endpoint** (optional) - Only needed for webhook export

## Step 1: Clone or Download the Repository

### Using Git (Recommended)

```bash
git clone https://github.com/yourusername/vcon-eleven-labs-adapter.git
cd vcon-eleven-labs-adapter
```

### Using Direct Download

Download the repository ZIP file and extract it, then navigate to the directory.

## Step 2: Create and Activate Virtual Environment

It's recommended to use a Python virtual environment to isolate dependencies.

### On macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### On Windows

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal prompt.

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs all required packages:
- vcon (vCon standardization)
- elevenlabs (ElevenLabs SDK)
- boto3 (AWS S3 support)
- requests (HTTP library)
- pydantic (Data validation)
- python-dotenv (Environment variables)
- pyyaml (Configuration)
- pytest (Testing framework)

### Install with Development Dependencies

If you plan to contribute or run tests:

```bash
pip install -e ".[dev]"
```

## Step 4: Verify Installation

### Quick Verification

```bash
python -c "import src; import vcon; import elevenlabs; print('All imports successful!')"
```

### Run Tests

```bash
pytest tests/ -v
```

You should see all tests pass.

## Step 5: Configure Environment

Create a `.env` file in the project root:

```bash
cp config.yml.example config.yml
```

Edit `config.yml` with your ElevenLabs API key and other settings (see [Configuration Guide](configuration.md)).

## Troubleshooting Installation

### Error: "Command not found: python3"

**Solution**: You may need to use `python` instead:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Error: "No module named venv"

**Solution**: Install venv module:
```bash
# On Ubuntu/Debian
sudo apt-get install python3-venv

# On macOS with Homebrew
brew install python3
```

### Error: "Permission denied" when installing

**Solution**: Try installing with `--user` flag:
```bash
pip install --user -r requirements.txt
```

### ImportError: No module named 'elevenlabs'

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Reinstall dependencies
```

### Tests Fail After Installation

**Solution**: Ensure the package is installed in development mode:
```bash
pip install -e .
pytest tests/ -v
```

## Next Steps

After successful installation:

1. **[Quick Start](quickstart.md)** - Get running in 5 minutes
2. **[Configuration](configuration.md)** - Configure your settings
3. **[User Guide](../02-usage/user-guide.md)** - Learn how to use the adapter

## Additional Resources

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [pip Documentation](https://pip.pypa.io/en/stable/)
- [vCon Specification](https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon/)
- [ElevenLabs API Docs](https://elevenlabs.io/docs/api)

---

**Version**: 1.0.0
**Last Updated**: October 17, 2025
