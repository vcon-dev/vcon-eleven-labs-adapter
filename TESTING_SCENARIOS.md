# Common Testing Scenarios & Debugging Guide

This guide covers common scenarios you might encounter and how to debug them.

## Scenario 1: First Time Setup

### What you want to do:
"I have a working ElevenLabs account with an agent on a phone number. I want to test the adapter for the first time."

### Steps:

```bash
# 1. Navigate to project
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

# 2. Run setup (one time)
bash setup_live_test.sh

# 3. Start testing
source venv/bin/activate
python3 test_live.py

# 4. Select option "1" to test connection
# This will list all your agents
```

### Expected output:
```
SUCCESS! Found 1 agent(s):

  1. Name: My Sales Agent
     ID: a1b2c3d4e5f6g7h8i9j0
     Phone: +1-555-0123

```

### If it fails:
- Check API key is correct
- Verify internet connection
- Ensure ElevenLabs service is up (check status.elevenlabs.io)

---

## Scenario 2: No Conversations Yet

### What you see:
"No conversations found for this agent"

### This is normal if:
1. You haven't placed any calls to your agent yet
2. ElevenLabs hasn't finished processing the call (takes 1-2 minutes)

### What to do:

```bash
# 1. Call your agent
# Dial the phone number shown in test_live.py (e.g., +1-555-0123)

# 2. Talk for at least 30 seconds
# Say hello, ask a question, have a conversation

# 3. Hang up

# 4. Wait 1-2 minutes for processing

# 5. Run test again
python3 test_live.py
# Select option "2" to check for conversations again
```

### Verify in ElevenLabs Dashboard:
1. Go to https://elevenlabs.io/app
2. Click on your agent
3. Check "Conversations" tab
4. You should see the call listed with status "Completed"

---

## Scenario 3: Verify API Connection Quickly

### One-liner to test connection:

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
source venv/bin/activate
export ELEVENLABS_API_KEY="your_key_here"

python3 -c "
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os
try:
    e = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
    agents = e.list_agents()
    print(f'SUCCESS: Found {len(agents)} agents')
except Exception as ex:
    print(f'ERROR: {ex}')
"
```

---

## Scenario 4: Process a Specific Agent

### When you have multiple agents and want to process just one:

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
source venv/bin/activate

python3 test_live.py

# Select option "3" - Process conversations
# When asked, select your specific agent from the list
```

### Or, manually specify in config.yml:

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  agent_ids:
    - your_specific_agent_id_here  # Replace with actual ID
  poll_interval: 300
```

Then run:
```bash
python3 examples/basic_usage.py
```

---

## Scenario 5: Debugging - View Detailed Logs

### Enable debug logging:

```bash
# Edit config.yml and change:
# logging:
#   level: DEBUG  <-- Change from INFO to DEBUG

cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
source venv/bin/activate

python3 examples/basic_usage.py

# View detailed logs
tail -f adapter.log
```

### Look for these in logs:

```
# Success indicators:
"Fetching agents from ElevenLabs API"
"Successfully fetched N agents"
"Fetching conversations for agent"
"Successfully created N vCons"

# Error indicators:
"ERROR"
"Exception"
"Failed"
"Timeout"
```

---

## Scenario 6: Check What Was Created

### View created vCon files:

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

# List all vCons
ls -lh vcons/

# Expected output:
# -rw-r--r--  1 user  group  12K Jan 15 14:32 vcon_20240115_143200_abc123.json

# Count of vCons
ls -1 vcons/vcon_*.json | wc -l

# View latest vCon (pretty printed)
cat vcons/vcon_*.json | python3 -m json.tool | head -100
```

### Inspect vCon details:

```bash
python3 << 'EOF'
import json
from pathlib import Path

vcon_dir = Path('./vcons')
vcon_files = sorted(vcon_dir.glob('vcon_*.json'), key=lambda x: x.stat().st_mtime)

if vcon_files:
    # Analyze latest vCon
    latest = vcon_files[-1]
    
    with open(latest) as f:
        vcon = json.load(f)
    
    print(f"File: {latest.name}")
    print(f"Size: {latest.stat().st_size / 1024:.2f} KB")
    print(f"\nContent Summary:")
    print(f"  UUID: {vcon.get('uuid', 'MISSING')}")
    print(f"  Subject: {vcon.get('subject', 'N/A')}")
    print(f"  Created: {vcon.get('created', 'MISSING')}")
    print(f"  Parties: {len(vcon.get('parties', []))}")
    
    parties = vcon.get('parties', [])
    for i, party in enumerate(parties):
        role = party.get('role', 'unknown')
        name = party.get('name', 'Unknown')
        print(f"    [{i}] {name} ({role})")
    
    print(f"\n  Dialog: {len(vcon.get('dialog', []))} entries")
    for i, dialog in enumerate(vcon.get('dialog', [])[:3]):
        dtype = dialog.get('type', 'unknown')
        parties_list = dialog.get('parties', [])
        print(f"    [{i}] Type: {dtype}, Parties: {parties_list}")
    
    print(f"\n  Attachments: {len(vcon.get('attachments', []))}")
    print(f"  Analysis: {len(vcon.get('analysis', []))}")

else:
    print("No vCon files found")
EOF
```

---

## Scenario 7: Handle Authentication Errors

### Error: "Invalid API key" or "Unauthorized"

**Debugging steps:**

```bash
# 1. Verify API key is set
echo "API Key: $ELEVENLABS_API_KEY"

# 2. Check for extra spaces or quotes
# The key should be exactly as shown in the dashboard
# No quotes, no extra spaces

# 3. Verify key is still valid
# - Go to https://elevenlabs.io/app/settings/api-keys
# - Check if key is still listed
# - Check if it's disabled
# - If unsure, generate a new one

# 4. Test with new key
export ELEVENLABS_API_KEY="new_key_here"
python3 test_live.py
```

---

## Scenario 8: Handle Network/Timeout Errors

### Error: "Connection timeout" or "Connection refused"

**Troubleshooting:**

```bash
# 1. Check internet connection
ping 8.8.8.8

# 2. Try increasing timeout in config.yml
# Change:
# elevenlabs:
#   timeout: 30
# To:
# elevenlabs:
#   timeout: 60

# 3. Check if ElevenLabs API is accessible
curl -s -H "Authorization: Bearer $ELEVENLABS_API_KEY" \
     https://api.elevenlabs.io/v1/agents | python3 -m json.tool

# 4. Check VPN or firewall
# If behind a corporate network, you might need VPN/proxy
```

---

## Scenario 9: No Dialog or Empty Conversations

### What you see:
"vCon created but has no dialog or very little content"

### Possible causes:

1. **Call was too short** - Make a longer call (30+ seconds)
2. **Call didn't process correctly** - Check ElevenLabs dashboard
3. **API didn't return dialog data** - This can happen if call data isn't fully indexed yet

### Debug:

```bash
# 1. Check raw API response
python3 << 'EOF'
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os
import json

extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()

if agents:
    agent_id = agents[0].id
    conversations = extractor.get_agent_conversations(agent_id)
    
    if conversations:
        conv = conversations[0]
        print(f"Conversation: {conv.id}")
        print(f"Duration: {conv.duration if hasattr(conv, 'duration') else 'N/A'}")
        print(f"Transcripts: {len(conv.transcripts) if hasattr(conv, 'transcripts') else 0}")
        print(f"Summary: {conv.summary if hasattr(conv, 'summary') else 'N/A'}")

EOF

# 2. Wait a bit longer and try again
# Some calls need extra time to fully process
# Wait 2-3 minutes and re-run
```

---

## Scenario 10: Permission/File Write Errors

### Error: "Permission denied" when saving vCons

**Solution:**

```bash
# 1. Check vcons directory permissions
ls -ld vcons/

# 2. Ensure vcons directory is writable
chmod 755 vcons/

# 3. Or create with proper permissions
rm -rf vcons/
mkdir -p vcons/
chmod 755 vcons/

# 4. Try processing again
python3 test_live.py
```

---

## Scenario 11: Testing Different Export Backends

### Test file export (local):

```bash
# Edit config.yml:
exporters:
  file:
    enabled: true
    directory: ./vcons

# vCons will be saved to ./vcons/
```

### Test webhook export (to external endpoint):

```bash
# Edit config.yml:
exporters:
  webhook:
    enabled: true
    url: https://your-webhook-endpoint.com/vcon
    api_key: your_webhook_key_if_needed

# When processing, vCons will be POSTed to webhook
```

### Test S3 export (to AWS):

```bash
# Edit config.yml:
exporters:
  s3:
    enabled: true
    bucket: my-vcon-bucket
    region: us-east-1
    prefix: elevenlabs/

# Configure AWS credentials:
aws configure

# Or set environment variables:
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
```

---

## Scenario 12: Testing Multiple Conversations

### Generate test data:

```bash
# Call your agent multiple times to create test data
# 1. Call 1: Say "hello"
# 2. Wait 2 minutes
# 3. Call 2: Ask a question
# 4. Wait 2 minutes
# 5. Call 3: Have a longer conversation
# 6. Wait 2 minutes

# Check results
python3 test_live.py
# Select option "2" to see all conversations
```

### Batch process:

```bash
# Process all conversations at once
python3 test_live.py
# Select option "5" for full test
# This will process all conversations for the agent
```

---

## Quick Debugging Checklist

When something doesn't work, check:

- [ ] API key is correct and not expired
- [ ] Internet connection is working
- [ ] ElevenLabs service is up
- [ ] Agent has actual conversations (place a test call)
- [ ] Virtual environment is activated
- [ ] Dependencies are installed (run setup_live_test.sh again)
- [ ] config.yml exists and is valid YAML
- [ ] vcons directory exists and is writable
- [ ] Check adapter.log for error messages
- [ ] Try with DEBUG logging enabled

## Getting More Help

1. **Check logs**: `tail -f adapter.log`
2. **Enable debug**: Set `level: DEBUG` in config.yml
3. **Read full guide**: See `LIVE_TESTING_GUIDE.md`
4. **ElevenLabs docs**: https://elevenlabs.io/docs
5. **vCon spec**: https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon/
