# Testing Resources & Getting Started

Complete guide to all available testing resources and how to use them.

## New Testing Resources Created

I've created comprehensive testing resources to help you configure and test the ElevenLabs vCon Adapter with your live account. Here's what's available:

### 1. Quick Start Guide (5 min read)
**File**: `QUICKSTART_LIVE_TEST.md`

Start here if you want to get up and running quickly.

- Step-by-step setup (2 minutes)
- Interactive testing tool instructions
- Quick command reference
- Basic troubleshooting

### 2. Complete Live Testing Guide (30 min read)
**File**: `LIVE_TESTING_GUIDE.md`

Comprehensive guide with all details and options.

- Prerequisites and setup
- Getting API key from ElevenLabs
- Configuration options explained
- Multiple testing methods
- Advanced testing scenarios
- Troubleshooting with solutions
- Quick reference commands

### 3. Interactive Testing Tool (Automated)
**File**: `test_live.py`

Guided interactive menu for testing.

Run: `python3 test_live.py`

Features:
- Prompts for API key
- Tests API connection
- Lists your agents
- Checks for conversations
- Processes conversations into vCons
- Verifies output files
- Full end-to-end test option

### 4. Setup Script (Automated)
**File**: `setup_live_test.sh`

One-time setup for dependencies and configuration.

Run: `bash setup_live_test.sh`

Does:
- Activates virtual environment
- Installs/verifies dependencies
- Creates config.yml
- Creates vcons output directory

### 5. Common Scenarios & Debugging (20 min read)
**File**: `TESTING_SCENARIOS.md`

Real-world scenarios and debugging approaches.

Includes:
- First time setup walkthrough
- Handling "no conversations" scenario
- Quick API connection test
- Multiple agents setup
- Debug logging techniques
- Checking created vCons
- Authentication error handling
- Network timeout solutions
- Permission/write error fixes
- Testing different export backends
- Quick debugging checklist

## Getting Started (Quick Path)

### For the Impatient (5 minutes)

```bash
# 1. Setup (one time only)
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
bash setup_live_test.sh

# 2. Test
source venv/bin/activate
python3 test_live.py

# 3. Follow the interactive menu
# Select option "5" for full test
```

### For Those Who Want Details (30 minutes)

```bash
# 1. Read the quick start
cat QUICKSTART_LIVE_TEST.md

# 2. Setup
bash setup_live_test.sh

# 3. Run test tool
source venv/bin/activate
python3 test_live.py
```

### For Thorough Understanding (1 hour)

```bash
# 1. Read quick start
cat QUICKSTART_LIVE_TEST.md

# 2. Read full guide
cat LIVE_TESTING_GUIDE.md

# 3. Read scenarios
cat TESTING_SCENARIOS.md

# 4. Setup and test
bash setup_live_test.sh
source venv/bin/activate
python3 test_live.py
```

## File Locations & Usage

### Setup & Tools
- **setup_live_test.sh** - Run once to set up everything
- **test_live.py** - Interactive tool for testing
- **config.yml.example** - Configuration template (auto-copied to config.yml)

### Documentation
- **QUICKSTART_LIVE_TEST.md** - 5-minute overview (start here)
- **LIVE_TESTING_GUIDE.md** - Complete reference (all details)
- **TESTING_SCENARIOS.md** - Real-world examples & debugging
- **TESTING_RESOURCES.md** - This file

### Configuration
- **config.yml** - Your adapter configuration (created by setup script)

### Output
- **vcons/** - Directory where vCon files are saved
- **adapter.log** - Debug logs from the adapter

## Prerequisites Checklist

Before starting, confirm:

- [ ] ElevenLabs account exists
- [ ] Agent created and connected to a phone number
- [ ] Python 3.8+ available
- [ ] Project cloned/available
- [ ] Virtual environment set up (already done)

## Quick Command Reference

```bash
# Setup (one time)
bash setup_live_test.sh

# Activate environment
source venv/bin/activate

# Run interactive test
python3 test_live.py

# Or run example script
python3 examples/basic_usage.py

# Check results
ls -lh vcons/

# View logs
tail -f adapter.log

# Test API connection only
export ELEVENLABS_API_KEY="your_key"
python3 -c "from src.extractors.elevenlabs_extractor import ElevenLabsExtractor; print('OK' if ElevenLabsExtractor('$ELEVENLABS_API_KEY').list_agents() else 'ERROR')"
```

## Expected Workflow

### Step 1: One-Time Setup (2 min)
```bash
bash setup_live_test.sh
```

### Step 2: Start Testing (2 min)
```bash
source venv/bin/activate
python3 test_live.py
```

### Step 3: First Run Without Conversations
- You'll see "No conversations found"
- This is normal - you need to place a test call

### Step 4: Generate Test Conversations
- Call your agent's phone number
- Have a conversation for 30+ seconds
- Wait 1-2 minutes for processing

### Step 5: Run Again to Process
- Run `python3 test_live.py` again
- Select option "5" for full test
- Choose your agent
- Adapter will process conversations into vCons

### Step 6: Verify Results
- Check `vcons/` directory
- View created vCon files
- Examine adapter.log for details

## Key Resources at a Glance

| Resource | Purpose | Time | How to Access |
|----------|---------|------|---------------|
| QUICKSTART_LIVE_TEST.md | Get started quickly | 5 min | `cat QUICKSTART_LIVE_TEST.md` |
| test_live.py | Interactive testing | real-time | `python3 test_live.py` |
| LIVE_TESTING_GUIDE.md | Complete reference | 30 min | `cat LIVE_TESTING_GUIDE.md` |
| TESTING_SCENARIOS.md | Debugging guide | 20 min | `cat TESTING_SCENARIOS.md` |
| setup_live_test.sh | Auto setup | 1 min | `bash setup_live_test.sh` |

## Common Starting Questions

### "Where do I start?"
Start with `QUICKSTART_LIVE_TEST.md`

### "I want a step-by-step guide"
Run `python3 test_live.py` - it's interactive and guides you

### "I'm stuck, what's wrong?"
Check `TESTING_SCENARIOS.md` - it has common issues and solutions

### "I want all the details"
Read `LIVE_TESTING_GUIDE.md`

### "Just set it up for me"
Run `bash setup_live_test.sh`

## Testing Checklist

Before you start testing, make sure you have:

1. [ ] ElevenLabs account with API key
2. [ ] Agent created and connected to phone number
3. [ ] Project directory available
4. [ ] Ran setup script: `bash setup_live_test.sh`
5. [ ] Ready to place test calls

## Success Indicators

You'll know it's working when:

1. `test_live.py` connects to ElevenLabs successfully
2. Your agents are listed with their IDs
3. After placing a test call, new conversations appear
4. Processing creates vCon files in `vcons/` directory
5. vCon files contain conversation data with parties and dialog

## Next Steps After Testing

Once live testing is successful:

1. **Automate**: Set up cron job to run adapter regularly
2. **Export**: Configure S3 or webhook exports
3. **Monitor**: Set up log aggregation
4. **Integrate**: Connect to your workflow/database
5. **Production**: Deploy to production environment

## Support & Help

If you need help:

1. **Quick questions**: Check TESTING_SCENARIOS.md
2. **Detailed help**: Read LIVE_TESTING_GUIDE.md
3. **Stuck?**: Enable DEBUG logging and check adapter.log
4. **API issues**: Check ElevenLabs docs: https://elevenlabs.io/docs
5. **vCon issues**: Check spec: https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon/

## Files Overview

### Main Documentation Files
```
QUICKSTART_LIVE_TEST.md      # Start here (5 min)
LIVE_TESTING_GUIDE.md        # Complete guide (reference)
TESTING_SCENARIOS.md         # Common scenarios & debug
TESTING_RESOURCES.md         # This file
```

### Tools & Scripts
```
setup_live_test.sh           # One-time setup script
test_live.py                 # Interactive test tool
examples/basic_usage.py      # Example usage script
```

### Configuration
```
config.yml.example           # Configuration template
config.yml                   # Your configuration (created)
```

### Output
```
vcons/                       # Created vCon files
adapter.log                  # Debug logs
```

## Version Information

These guides are for:
- ElevenLabs vCon Adapter v1.0+
- Python 3.8+
- vCon format (RFC draft)
- ElevenLabs API v1

---

**Last Updated**: January 2024
**Status**: Complete and ready to use
