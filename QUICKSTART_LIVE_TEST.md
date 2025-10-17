# Quick Start: Live Testing Guide

Get your ElevenLabs vCon Adapter up and running in 5 minutes.

## Prerequisites Checklist

Before starting, confirm you have:

- [x] ElevenLabs account with an agent
- [x] Agent connected to a phone number
- [x] ElevenLabs API key (or know where to get it)
- [x] Python 3.8+ with venv already set up
- [x] This project cloned

## Step-by-Step Setup

### 1. Run Initial Setup (2 minutes)

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

# Run setup script (one time only)
bash setup_live_test.sh
```

This will:
- Activate the virtual environment
- Install dependencies
- Create config.yml
- Create vcons output directory

### 2. Get Your API Key (1 minute)

1. Go to: https://elevenlabs.io/app/settings/api-keys
2. Create or copy your API key
3. Keep it safe

### 3. Start Interactive Testing (2 minutes)

```bash
# Make sure you're in the project directory
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

# Activate the virtual environment
source venv/bin/activate

# Run the interactive test tool
python3 test_live.py
```

### 4. Follow the Interactive Menu

The tool will guide you through:

1. **Enter your API key** - Paste your API key when prompted
2. **Test connection** - Verify your ElevenLabs account is accessible
3. **List agents** - See all your agents and their IDs
4. **Check conversations** - See if your agent has any recent calls
5. **Process conversations** - Convert them to vCons
6. **View results** - Check the created vCon files

## If You Don't Have Conversations Yet

If the tool shows "No conversations found":

1. **Call your agent**: Dial the phone number attached to your ElevenLabs agent
2. **Have a conversation**: Talk to the AI agent for 30+ seconds
3. **Wait**: Let ElevenLabs process the call (1-2 minutes)
4. **Run test again**: Re-run `python3 test_live.py` and check again

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Set API key for current session
export ELEVENLABS_API_KEY="your_api_key_here"

# Run interactive test tool
python3 test_live.py

# Run example script
python3 examples/basic_usage.py

# Check created vCons
ls -lh vcons/

# View latest vCon
cat vcons/vcon_*.json | python3 -m json.tool | head -50

# View logs
tail -f adapter.log

# Deactivate virtual environment
deactivate
```

## Verify Success

You'll know it's working when you see:

1. vCon files created in `./vcons/` directory
2. Filenames like: `vcon_20231215_143022_abc123.json`
3. Each file contains conversation data in vCon format

## Troubleshooting

### "No conversations found"
- You need to place a call to your agent first
- Wait 1-2 minutes for processing
- Verify in ElevenLabs dashboard that call appears

### "API Key Invalid"
- Double-check your API key at https://elevenlabs.io/app/settings/api-keys
- Make sure there are no extra spaces
- Regenerate if necessary

### "Command not found: python3"
- Ensure Python 3.8+ is installed
- Try using `python` instead of `python3`

### "ModuleNotFoundError"
- Activate virtual environment: `source venv/bin/activate`
- Re-run setup: `bash setup_live_test.sh`

## Next Steps

After successful testing:

1. **Read Full Documentation**: See `LIVE_TESTING_GUIDE.md` for advanced options
2. **Configure Exports**: Set up S3 or webhook exports if needed
3. **Automate Processing**: Schedule regular runs with cron
4. **Monitor**: Check `adapter.log` for any issues

## Full Documentation

For detailed configuration and troubleshooting, see:
- `LIVE_TESTING_GUIDE.md` - Comprehensive live testing guide
- `README.md` - Project overview
- `config.yml.example` - All configuration options

## Getting Help

Need help? Check:
1. `adapter.log` for error details
2. `LIVE_TESTING_GUIDE.md` troubleshooting section
3. ElevenLabs docs: https://elevenlabs.io/docs
