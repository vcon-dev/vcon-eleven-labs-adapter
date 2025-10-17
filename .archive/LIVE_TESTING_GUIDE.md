# Live Testing Guide: ElevenLabs vCon Adapter

This guide walks you through configuring and testing the adapter with your real ElevenLabs account connected to a phone number and agent.

## Prerequisites

Before you begin, ensure you have:

1. **ElevenLabs Account**: With an agent already created and connected to a phone number
2. **ElevenLabs API Key**: Generate this from your ElevenLabs dashboard
3. **Python Environment**: The virtual environment is already set up in this project
4. **Agent ID**: You'll need your agent's ID from ElevenLabs

## Step 1: Get Your ElevenLabs API Key

1. Log into your ElevenLabs dashboard at https://elevenlabs.io/app
2. Navigate to **API Keys** or **Settings** > **API Keys**
3. Create a new API key or copy your existing one
4. Keep this key secure - you'll use it next

## Step 2: Identify Your Agent ID

1. Go to your ElevenLabs dashboard
2. Navigate to **Agents** section
3. Find your agent connected to the phone number
4. Copy the Agent ID (usually a long alphanumeric string)
5. Note the phone number associated with the agent

## Step 3: Configure Environment Variables

Create a `.env` file in the project root (or set these in your shell):

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

# Create .env file
cat > .env << 'EOF'
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_AGENT_IDS=your_agent_id_here
LOG_LEVEL=DEBUG
EOF
```

Export the environment variable:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

Alternatively, set it directly in the config file (see Step 4).

## Step 4: Configure the Adapter

Copy the example configuration and customize it:

```bash
cp config.yml.example config.yml
```

Edit `config.yml` and update:

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}  # Or directly: your_api_key_here
  agent_ids: all                   # Or: [your_agent_id_here]
  poll_interval: 300               # Check every 5 minutes
  batch_size: 10
  timeout: 30

exporters:
  file:
    enabled: true
    directory: ./vcons
    overwrite: false

logging:
  level: DEBUG  # Use DEBUG for detailed output during testing
  file: adapter.log
  console: true
  format: text  # Use 'text' for easier reading during testing
```

### Configuration Options Explained

- **api_key**: Your ElevenLabs API key (use environment variable or hardcode)
- **agent_ids**: 
  - Use `all` to process all agents
  - Use `[agent_id_1, agent_id_2]` for specific agents
- **poll_interval**: How often to check for new conversations (in seconds)
- **batch_size**: Number of conversations to fetch per API call
- **timeout**: Request timeout in seconds
- **directory**: Where to save vCon files locally

## Step 5: Test API Connection

Before processing conversations, verify your API key works:

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

# Activate virtual environment
source venv/bin/activate

# Run a quick connection test
python3 << 'EOF'
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os

api_key = os.getenv('ELEVENLABS_API_KEY', 'your_api_key_here')

try:
    extractor = ElevenLabsExtractor(api_key=api_key)
    agents = extractor.list_agents()
    print(f"SUCCESS! Found {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.name} (ID: {agent.id})")
except Exception as e:
    print(f"ERROR: {e}")
    print("Check your API key and internet connection")
EOF
```

## Step 6: Generate Test Conversations

To test the adapter effectively, you need actual conversations:

1. **Place a call to your agent**:
   - Call the phone number attached to your ElevenLabs agent
   - Have a brief conversation
   - End the call gracefully

2. **Wait for processing**:
   - The ElevenLabs API typically processes calls within 1-2 minutes
   - Conversations may take a few minutes to appear in the API

3. **Verify in ElevenLabs Dashboard**:
   - Log into ElevenLabs
   - Check your agent's conversation history
   - Confirm the call appears with status "completed"

## Step 7: Run the Adapter

### Option A: Process All Conversations for All Agents

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
source venv/bin/activate

python3 << 'EOF'
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')

print("Adapter Metrics:")
print(adapter.get_metrics())

print("\nProcessing all agents...")
vcons = adapter.process_all()

print(f"\nSUCCESS! Created {len(vcons)} vCons")
for vcon in vcons:
    print(f"  - {vcon.uuid}")

print("\nvCons saved to ./vcons/ directory")
EOF
```

### Option B: Process Specific Agent

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
source venv/bin/activate

python3 << 'EOF'
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')

agent_id = "your_agent_id_here"  # Replace with your actual agent ID
print(f"Processing agent: {agent_id}...")

vcons = adapter.process_agent(agent_id)

print(f"Created {len(vcons)} vCons for agent {agent_id}")
for vcon in vcons:
    print(f"  - {vcon.uuid}")
EOF
```

### Option C: Use the Example Script

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
source venv/bin/activate

python3 examples/basic_usage.py
```

## Step 8: Verify Output

Check the vCons were created successfully:

```bash
# List created vCon files
ls -lh ./vcons/

# View a vCon file
cat ./vcons/vcon_*.json | python3 -m json.tool | head -100

# Get count of created vCons
ls -1 ./vcons/vcon_*.json | wc -l
```

## Step 9: Examine vCon Structure

View the details of a created vCon:

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

python3 << 'EOF'
import json
from pathlib import Path

vcon_dir = Path('./vcons')
vcon_files = list(vcon_dir.glob('vcon_*.json'))

if vcon_files:
    latest_vcon = sorted(vcon_files, key=lambda x: x.stat().st_mtime)[-1]
    
    with open(latest_vcon) as f:
        vcon_data = json.load(f)
    
    print(f"vCon File: {latest_vcon.name}")
    print(f"UUID: {vcon_data.get('uuid')}")
    print(f"Subject: {vcon_data.get('subject', 'N/A')}")
    print(f"Parties: {len(vcon_data.get('parties', []))}")
    
    for i, party in enumerate(vcon_data.get('parties', [])):
        print(f"  Party {i}: {party.get('name', 'Unknown')} ({party.get('role', 'unknown')})")
    
    print(f"\nDialog Entries: {len(vcon_data.get('dialog', []))}")
    for i, dialog in enumerate(vcon_data.get('dialog', [])[:3]):  # Show first 3
        print(f"  {i+1}. Type: {dialog.get('type')}, Parties: {dialog.get('parties')}")
    
    print(f"\nAttachments: {len(vcon_data.get('attachments', []))}")
    print(f"Analysis: {len(vcon_data.get('analysis', []))}")
    
else:
    print("No vCon files found in ./vcons/")
EOF
```

## Troubleshooting

### Issue: "API Key Invalid"

**Solution**:
```bash
# Verify your API key is set correctly
echo $ELEVENLABS_API_KEY

# Make sure it's not quoted when exporting
export ELEVENLABS_API_KEY=your_actual_key_without_quotes
```

### Issue: "No Conversations Found"

**Possible causes**:
1. No calls have been made to your agent yet
2. Calls haven't been processed by ElevenLabs yet (wait 2-3 minutes)
3. Wrong agent ID in configuration

**Solution**:
```bash
# Verify your agent ID
python3 << 'EOF'
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os

extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()
for agent in agents:
    print(f"Agent: {agent.name}")
    print(f"  ID: {agent.id}")
    print(f"  Phone: {agent.phone_number if hasattr(agent, 'phone_number') else 'N/A'}")
EOF
```

### Issue: "Connection Timeout"

**Solution**:
- Increase the timeout in `config.yml`:
  ```yaml
  elevenlabs:
    timeout: 60  # Increased from 30
  ```

### Issue: ImportError for elevenlabs

**Solution**:
```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter
source venv/bin/activate

pip install elevenlabs
pip install -r requirements.txt
```

### Issue: vCon Files Not Created

**Troubleshooting**:
```bash
# Enable DEBUG logging to see what's happening
# Edit config.yml and set: level: DEBUG

# Then re-run and check adapter.log
tail -f adapter.log

# Look for errors related to export or vCon building
grep -i error adapter.log
```

## Advanced Testing

### Test with Multiple Agents

Edit `config.yml`:

```yaml
elevenlabs:
  agent_ids: 
    - agent_id_1
    - agent_id_2
    - agent_id_3
```

Then run:
```bash
python3 examples/basic_usage.py
```

### Test Export to Multiple Backends

Edit `config.yml` to enable multiple exporters:

```yaml
exporters:
  file:
    enabled: true
    directory: ./vcons
  
  # S3 export (requires AWS credentials)
  s3:
    enabled: false  # Set to true if configured
    bucket: my-bucket
    region: us-east-1
  
  # Webhook export (requires webhook endpoint)
  webhook:
    enabled: false  # Set to true if you have a webhook
    url: https://your-webhook-endpoint.com/vcon
```

### Monitor with Verbose Logging

```bash
cd /Users/thomashowe/Documents/GitHub/vcon_eleven_labs_adapter

python3 << 'EOF'
import logging
from src.adapter import ElevenLabsVconAdapter

# Set verbose logging
logging.basicConfig(level=logging.DEBUG)

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

print(f"Processed {len(vcons)} vCons")
EOF
```

## Next Steps

After successful live testing:

1. **Validate vCon Output**: Ensure all vCons are valid according to the vCon specification
2. **Test Export Backends**: 
   - Try exporting to S3 or webhook if needed
   - Verify exported vCons can be retrieved
3. **Set Up Monitoring**: 
   - Configure scheduled processing
   - Set up log aggregation
   - Monitor for errors
4. **Production Deployment**:
   - Use secure credential management (AWS Secrets Manager, etc.)
   - Set up database to track processed conversations
   - Implement retry logic for failed exports

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate

# Set API key
export ELEVENLABS_API_KEY="your_key"

# Test connection
python3 -c "from src.extractors.elevenlabs_extractor import ElevenLabsExtractor; import os; ElevenLabsExtractor(os.getenv('ELEVENLABS_API_KEY')).list_agents()"

# Run adapter
python3 examples/basic_usage.py

# Check output
ls -lh ./vcons/

# View logs
tail -f adapter.log

# Run tests
pytest tests/ -v
```

## Getting Help

If you encounter issues:

1. Check `adapter.log` for detailed error messages
2. Enable DEBUG logging in `config.yml`
3. Review the ElevenLabs API documentation: https://elevenlabs.io/docs
4. Check the vCon specification: https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon/
