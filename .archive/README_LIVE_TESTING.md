# Live Testing Guide Summary

Everything you need to configure and test the ElevenLabs vCon Adapter with your real account.

## What You Have

Complete testing infrastructure with:
- Interactive testing tool with menu-driven interface
- Automated setup scripts
- Comprehensive documentation
- Real-world scenarios and debugging guides
- Quick reference guides

## The Fastest Path to Success (10 minutes)

```bash
# 1. Setup (2 min)
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
bash setup_live_test.sh

# 2. Test (2 min)
source venv/bin/activate
python3 test_live.py

# 3. Get API key (1 min)
# Visit: https://elevenlabs.io/app/settings/api-keys

# 4. Follow the interactive menu (5 min)
# Select "5" for complete test
```

## Documentation Map

| File | Purpose | Read Time | Start Here? |
|------|---------|-----------|------------|
| **QUICKSTART_LIVE_TEST.md** | Fast overview | 5 min | **YES** |
| **test_live.py** | Interactive tool | Real-time | YES (after quickstart) |
| **LIVE_TESTING_GUIDE.md** | Complete reference | 30 min | Use as reference |
| **TESTING_SCENARIOS.md** | Debug guide | 20 min | When stuck |
| **TESTING_RESOURCES.md** | Resource summary | 10 min | Overview |

## Quick Start Checklist

- [ ] Have ElevenLabs account with agent on phone number
- [ ] Know where to get API key (https://elevenlabs.io/app/settings/api-keys)
- [ ] Run: `bash setup_live_test.sh`
- [ ] Run: `python3 test_live.py`
- [ ] Select option "1" to test connection
- [ ] Enter API key when prompted
- [ ] See your agents listed
- [ ] Place test call to your agent's phone number
- [ ] Wait 2 minutes for processing
- [ ] Run test again, select option "5"
- [ ] Check `vcons/` directory for created files

## What Happens When You Run the Tests

### First Run (No Conversations Yet)
```
Test Result: No conversations found for this agent

Next Steps:
1. Call your agent's phone number
2. Have a conversation (30+ seconds)
3. Wait 1-2 minutes for processing
4. Run test again
```

### After You Place Test Calls
```
Test Result: Found 1 conversation(s)

Processing...
Successfully created 1 vCon

vCon Details:
- UUID: [unique ID]
- Subject: [conversation subject]
- Parties: 2
- Dialog: 10 entries

vCon saved to: ./vcons/vcon_20240115_143200_abc123.json
```

## The Tools You Have

### 1. Interactive Test Tool (Recommended)
```bash
python3 test_live.py
```
Menu-driven interface that guides you through all steps.

**Options:**
- Option 1: Test API connection (lists agents)
- Option 2: Check for conversations
- Option 3: Process conversations to vCons
- Option 4: Verify created vCon files
- Option 5: Full test (1-4 all together)

### 2. Setup Script (One-time)
```bash
bash setup_live_test.sh
```
Prepares environment and creates config.

### 3. Example Script
```bash
python3 examples/basic_usage.py
```
Direct usage example.

## Common Scenarios

### Scenario: "No conversations found"
**Normal for first run.** You need to:
1. Call your agent's phone number
2. Have a conversation for 30+ seconds
3. Wait 1-2 minutes for processing
4. Run test again

See: `TESTING_SCENARIOS.md` - Scenario 2

### Scenario: "API Key Invalid"
**Check:**
1. API key has no extra spaces
2. Key not expired (regenerate if needed)
3. From right dashboard (https://elevenlabs.io/app/settings/api-keys)

See: `TESTING_SCENARIOS.md` - Scenario 7

### Scenario: "Connection timeout"
**Try:**
1. Check internet connection: `ping 8.8.8.8`
2. Increase timeout in config.yml: `timeout: 60`
3. Verify ElevenLabs is accessible

See: `TESTING_SCENARIOS.md` - Scenario 8

## Files Created

### After Running `setup_live_test.sh`
- `config.yml` - Your configuration (created from template)
- `vcons/` - Directory for output vCon files

### After Running `test_live.py`
- `vcons/vcon_*.json` - Your created vCon files
- `adapter.log` - Debug and operation logs

## Success Indicators

You'll know it's working when:

1. ✓ `test_live.py` connects successfully to ElevenLabs
2. ✓ Your agent is listed with ID
3. ✓ After test calls, conversations appear
4. ✓ Processing completes without errors
5. ✓ Files appear in `vcons/` directory
6. ✓ Files are > 1 KB and contain valid JSON
7. ✓ `adapter.log` shows successful operations

## Getting Help

**Quick question?** → `cat TESTING_SCENARIOS.md`

**Want details?** → `cat LIVE_TESTING_GUIDE.md`

**Still stuck?**
1. Enable DEBUG logging in config.yml
2. Check `adapter.log` for errors
3. Re-read TESTING_SCENARIOS.md

**External help:**
- ElevenLabs API docs: https://elevenlabs.io/docs
- vCon spec: https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon/

## Configuration Quick Reference

### File: `config.yml`

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}  # Your API key
  agent_ids: all                   # Process all agents
  timeout: 30                      # Request timeout

exporters:
  file:
    enabled: true                  # Save locally
    directory: ./vcons             # Output directory
```

**Environment variable (alternative to config):**
```bash
export ELEVENLABS_API_KEY="your_key_here"
```

## Commands Reference

```bash
# Navigation
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

# Setup (one time)
bash setup_live_test.sh

# Activate environment
source venv/bin/activate

# Run interactive test (main tool)
python3 test_live.py

# Run example
python3 examples/basic_usage.py

# View results
ls -lh vcons/
cat vcons/vcon_*.json | python3 -m json.tool | head -50

# View logs
tail -f adapter.log
grep -i error adapter.log

# Deactivate
deactivate
```

## Workflow Diagram

```
1. Setup (2 min)
   bash setup_live_test.sh
   
2. Start Test (1 min)
   python3 test_live.py
   
3. Enter API Key (1 min)
   → Paste your API key
   
4. Test Connection (1 min)
   ✓ Connection successful
   ✓ Agents listed
   
5. Check Conversations (1 min)
   → No conversations found
   → Need to place test call
   
6. Place Test Call (1-2 min)
   → Call agent's phone number
   → Have conversation
   → Wait 1-2 minutes
   
7. Re-run Test (1 min)
   python3 test_live.py
   
8. Process Conversations (1 min)
   ✓ Processing complete
   ✓ vCons created
   
9. Verify Results (1 min)
   ✓ Files in vcons/
   ✓ Success!
```

## Next Steps After Testing

1. **Automate**: Set up cron job for regular processing
2. **Configure Exports**: Add S3 or webhook exports
3. **Monitor**: Set up alerts for errors
4. **Integrate**: Connect to your systems
5. **Deploy**: Move to production

## Timeline

| Step | Time | What Happens |
|------|------|--------------|
| Setup | 2 min | Install dependencies, create config |
| API Test | 1 min | Verify connection to ElevenLabs |
| First Test | 1 min | Check for conversations (none yet) |
| Test Call | 2 min | You call your agent |
| Wait | 2 min | ElevenLabs processes the call |
| Re-test | 1 min | Check for new conversations |
| Processing | 1 min | Adapter converts to vCons |
| Verify | 1 min | Check created files |
| **Total** | **11 min** | Complete working system |

## Verification Command

Quick one-liner to check everything works:

```bash
source venv/bin/activate && \
export ELEVENLABS_API_KEY="your_key" && \
python3 -c "
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
e = ElevenLabsExtractor('your_key')
agents = e.list_agents()
print(f'SUCCESS: Found {len(agents)} agents')
for a in agents: print(f'  - {a.name} (ID: {a.id})')
"
```

## Support Resources

- **Quick Start**: QUICKSTART_LIVE_TEST.md
- **Complete Guide**: LIVE_TESTING_GUIDE.md
- **Debugging**: TESTING_SCENARIOS.md
- **Resources**: TESTING_RESOURCES.md
- **This File**: README_LIVE_TESTING.md

---

**Ready to start?**

```bash
bash setup_live_test.sh
source venv/bin/activate
python3 test_live.py
```

Good luck!
