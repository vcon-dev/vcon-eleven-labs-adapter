# Quick Start: 5 Minutes to Running

Get the vCon ElevenLabs Adapter up and running in just 5 minutes!

## Prerequisites Checklist

- [x] Python 3.8+ installed
- [x] ElevenLabs account with an agent
- [x] ElevenLabs API key (from https://elevenlabs.io/app/settings/api-keys)
- [x] Agent connected to a phone number

## Step 1: Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/vcon-eleven-labs-adapter.git
cd vcon-eleven-labs-adapter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (1 minute)

```bash
# Copy example configuration
cp config.yml.example config.yml

# Edit config.yml and add your API key:
# elevenlabs:
#   api_key: your_api_key_here
```

Or set it as an environment variable:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

## Step 3: Run (2 minutes)

### Option A: Interactive Testing

```bash
python3 test_live.py
```

Follow the interactive menu to:
1. Test API connection
2. List your agents
3. Check conversations
4. Process conversations to vCons

### Option B: Run Example Script

```bash
python3 examples/basic_usage.py
```

This processes all conversations from your agents into vCon format.

### Option C: Run Tests

```bash
pytest tests/ -v
```

All tests should pass.

## Verify Success

Check the created vCon files:

```bash
# List created vCons
ls -lh vcons/

# View the latest vCon
cat vcons/vcon_*.json | python3 -m json.tool | head -50
```

You should see vCon files like:
```
vcon_20251017_150001_abc123.json
vcon_20251017_150002_def456.json
```

## Common Commands

```bash
# Activate environment
source venv/bin/activate

# Set API key
export ELEVENLABS_API_KEY="your_key"

# Run interactive test
python3 test_live.py

# Run example
python3 examples/basic_usage.py

# Run tests
pytest

# View logs
tail -f adapter.log

# Deactivate environment
deactivate
```

## No Conversations Yet?

If you don't have conversations yet:

1. **Call your agent** - Use the phone number shown in your ElevenLabs dashboard
2. **Talk for 30+ seconds** - Have a brief conversation with the AI agent
3. **Wait 1-2 minutes** - Let ElevenLabs process the call
4. **Run again** - Re-run the adapter to process the new conversation

## Next Steps

- **[Full Configuration Guide](configuration.md)** - Configure all options
- **[User Guide](../02-usage/user-guide.md)** - Complete usage documentation
- **[Testing Guide](../03-testing/testing-guide.md)** - Run comprehensive tests
- **[Troubleshooting](../03-testing/scenarios.md)** - Debug common issues

## Getting Help

- Check `adapter.log` for detailed logs
- See [Debugging Guide](../03-testing/scenarios.md)
- Review [Examples](../02-usage/examples.md)

---

**That's it! You're now running the vCon ElevenLabs Adapter.**

For more advanced configuration and usage, see the full documentation.
