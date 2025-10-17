# Live Testing with ElevenLabs

Test the adapter with your real ElevenLabs account and agents.

## Prerequisites

- ElevenLabs account with active agent
- Agent connected to a phone number
- ElevenLabs API key
- Recent conversations (or ability to place test calls)

## Step 1: Configure API Key

Set your ElevenLabs API key as an environment variable:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

Or edit `config.yml`:

```yaml
elevenlabs:
  api_key: your_api_key_here
```

## Step 2: Verify API Connection

Test your API key works:

```bash
python3 << 'EOF'
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os

extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()

print(f"SUCCESS! Found {len(agents)} agents:")
for agent in agents:
    print(f"  - {agent.name} (ID: {agent.id})")
EOF
```

**Expected Output:**
```
SUCCESS! Found 1 agents:
  - My Sales Agent (ID: agent_12345...)
```

## Step 3: Check for Conversations

Get conversations for your agent:

```bash
python3 << 'EOF'
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os

extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()

if agents:
    agent_id = agents[0].id
    conversations = extractor.get_agent_conversations(agent_id)
    print(f"Agent '{agents[0].name}' has {len(conversations)} conversations")
else:
    print("No agents found")
EOF
```

## Step 4: Run Interactive Test

Run the interactive test tool:

```bash
python3 test_live.py
```

Follow the menu to:
1. Test API connection
2. List agents
3. View conversations
4. Process conversations
5. View results

## Step 5: Process Conversations

### Option A: Using Interactive Tool

```bash
python3 test_live.py
# Select option 3 or 5
```

### Option B: Using Example Script

```bash
python3 examples/basic_usage.py
```

### Option C: Using Adapter Directly

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

print(f"Created {len(vcons)} vCons")
for vcon in vcons:
    print(f"  UUID: {vcon.uuid}")
```

## Step 6: Verify Output

Check created vCon files:

```bash
# List files
ls -lh vcons/

# View latest
cat vcons/vcon_*.json | python3 -m json.tool | head -100
```

## Step 7: Enable Debug Logging

For detailed debugging:

1. Edit `config.yml`:
   ```yaml
   logging:
     level: DEBUG  # Change from INFO
   ```

2. Re-run processing:
   ```bash
   python3 examples/basic_usage.py
   ```

3. Check logs:
   ```bash
   tail -f adapter.log
   ```

## Generate Test Data

If you don't have conversations yet:

1. **Call your agent** - Use the phone number from ElevenLabs dashboard
2. **Talk for 30+ seconds** - Have a brief conversation
3. **Wait 1-2 minutes** - Let ElevenLabs process
4. **Check results** - Run test again

## Common Test Scenarios

### Test With Multiple Agents

Configure multiple agents:

```yaml
elevenlabs:
  agent_ids:
    - agent_1_id
    - agent_2_id
    - agent_3_id
```

Process all:

```bash
python3 examples/basic_usage.py
```

### Test Specific Agent

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Process specific agent
agent_id = "your_agent_id"
vcons = adapter.process_agent(agent_id)

print(f"Created {len(vcons)} vCons for agent {agent_id}")
```

### Test Multiple Export Backends

Configure all exporters:

```yaml
exporters:
  file:
    enabled: true
    directory: ./vcons
  
  s3:
    enabled: true
    bucket: my-bucket
    region: us-east-1
  
  webhook:
    enabled: true
    url: https://example.com/webhook
```

Process:

```bash
python3 examples/basic_usage.py
```

All exporters will export automatically.

## Monitor Processing

Check metrics during processing:

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

# Get metrics
metrics = adapter.get_metrics()

print("Processing Metrics:")
print(f"  Agents: {metrics.get('agents_processed', 0)}")
print(f"  Conversations: {metrics.get('conversations_found', 0)}")
print(f"  vCons: {metrics.get('vcons_created', 0)}")
print(f"  Exports: {metrics.get('exports_successful', 0)}")
print(f"  Time: {metrics.get('processing_time', 0):.2f}s")
```

## Troubleshooting Live Tests

### "API Key Invalid"

```bash
# Verify key
echo $ELEVENLABS_API_KEY

# Get new key from:
# https://elevenlabs.io/app/settings/api-keys
```

### "No Conversations Found"

1. Verify agent in ElevenLabs dashboard
2. Place a test call to your agent
3. Wait 1-2 minutes for processing
4. Check ElevenLabs dashboard for the call
5. Re-run test

### "Connection Timeout"

```yaml
elevenlabs:
  timeout: 60  # Increase from 30
```

### vCons Not Created

Check logs:
```bash
tail -f adapter.log
grep ERROR adapter.log
```

Enable DEBUG:
```yaml
logging:
  level: DEBUG
```

## Performance Testing

### Test with Large Number of Conversations

```python
from src.adapter import ElevenLabsVconAdapter
import time

start = time.time()

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

duration = time.time() - start

print(f"Processed {len(vcons)} vCons in {duration:.2f}s")
print(f"Rate: {len(vcons)/duration:.2f} vCons/second")
```

### Monitor Memory Usage

```bash
# Run with memory profiling
pip install memory-profiler

python3 -m memory_profiler examples/basic_usage.py
```

## Validate vCon Output

Verify created vCons are valid:

```python
import json
from pathlib import Path

vcon_dir = Path('./vcons')

for vcon_file in vcon_dir.glob('vcon_*.json'):
    with open(vcon_file) as f:
        vcon_data = json.load(f)
    
    # Check required fields
    assert vcon_data.get('uuid'), f"Missing UUID: {vcon_file}"
    assert vcon_data.get('parties'), f"Missing parties: {vcon_file}"
    assert vcon_data.get('dialog'), f"Missing dialog: {vcon_file}"
    
    print(f"✓ {vcon_file.name} is valid")
```

## Next Steps

After successful live testing:

1. **Configure Exports** - Set up S3 or webhook if needed
2. **Schedule Processing** - Set up automated runs
3. **Monitor Logs** - Check for errors regularly
4. **Validate Data** - Ensure vCons are correct
5. **Deploy** - Move to production

---

For more information:
- [Testing Guide](testing-guide.md)
- [Debugging Guide](scenarios.md)
- [User Guide](../02-usage/user-guide.md)
