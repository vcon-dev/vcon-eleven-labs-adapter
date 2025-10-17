# Debugging & Common Scenarios

Practical debugging guidance for common issues and scenarios.

## Quick Debugging Checklist

When something doesn't work:

- [ ] Check `adapter.log` for error messages
- [ ] Verify API key is correct and not expired
- [ ] Check internet connection
- [ ] Ensure virtual environment is activated
- [ ] Verify configuration file exists and is valid YAML
- [ ] Check directory permissions for file export
- [ ] Enable DEBUG logging for more details

## Common Issues and Solutions

### Issue: "No Conversations Found"

**When you see this:**
```
No conversations found for agent
```

**Possible Causes:**
1. Agent has no calls yet
2. Calls haven't finished processing (takes 1-2 minutes)
3. Wrong agent ID in configuration

**Solution:**

```bash
# 1. Verify agent ID
python3 << 'EOF'
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os

extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()
for agent in agents:
    print(f"Agent: {agent.name} (ID: {agent.id})")
EOF

# 2. Place a test call
# Call your agent's phone number

# 3. Wait 1-2 minutes for processing

# 4. Run test again
python3 test_live.py
```

### Issue: "Invalid API Key"

**When you see this:**
```
401 Unauthorized - Invalid API key
```

**Solution:**

1. Verify API key:
   ```bash
   echo $ELEVENLABS_API_KEY
   # Should print your actual API key (no quotes, no spaces)
   ```

2. Get new key if needed:
   - Go to https://elevenlabs.io/app/settings/api-keys
   - Copy the key exactly
   - No extra spaces or quotes

3. Set environment variable:
   ```bash
   export ELEVENLABS_API_KEY="your_key_without_extra_spaces"
   ```

### Issue: "Connection Timeout"

**When you see this:**
```
ConnectionError: Connection timeout
```

**Causes:**
- Network is slow
- API is slow responding
- Firewall/proxy blocking connection

**Solution:**

1. Increase timeout in `config.yml`:
   ```yaml
   elevenlabs:
     timeout: 60  # Increase from 30
   ```

2. Check network:
   ```bash
   ping 8.8.8.8
   ```

3. Try with verbose logging:
   ```yaml
   logging:
     level: DEBUG
   ```

### Issue: "Module Not Found"

**When you see this:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install in development mode
pip install -e .

# Run tests
pytest
```

### Issue: "Permission Denied" on vCon Export

**When you see this:**
```
PermissionError: [Errno 13] Permission denied: './vcons'
```

**Solution:**

```bash
# Check directory exists
ls -ld vcons/

# Ensure directory is writable
chmod 755 vcons/

# Or recreate directory
rm -rf vcons/
mkdir -p vcons/
chmod 755 vcons/
```

### Issue: "Config File Not Found"

**When you see this:**
```
FileNotFoundError: config.yml
```

**Solution:**

```bash
# Create config from example
cp config.yml.example config.yml

# Edit with your settings
nano config.yml
```

### Issue: "vCon Files Not Created"

**When you see this:**
```
Created 0 vCons
```

**Troubleshooting:**

1. Check logs:
   ```bash
   tail -f adapter.log
   ```

2. Enable DEBUG logging:
   ```yaml
   logging:
     level: DEBUG
   ```

3. Verify conversations exist:
   ```python
   from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
   import os

   extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
   agents = extractor.list_agents()
   if agents:
       conversations = extractor.get_agent_conversations(agents[0].id)
       print(f"Found {len(conversations)} conversations")
   ```

### Issue: "S3 Upload Failed"

**When you see this:**
```
S3UploadError: An error occurred
```

**Solution:**

1. Verify AWS credentials:
   ```bash
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_SECRET_ACCESS_KEY
   ```

2. Check bucket exists and is accessible:
   ```bash
   aws s3 ls s3://your-bucket/
   ```

3. Verify bucket permissions (allow PutObject)

4. Check configuration:
   ```yaml
   exporters:
     s3:
       bucket: your-bucket-name
       region: us-east-1
   ```

### Issue: "Webhook Export Failing"

**When you see this:**
```
WebhookError: Failed to post vCon
```

**Solution:**

1. Test webhook endpoint manually:
   ```bash
   curl -X POST https://your-webhook.com/endpoint \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

2. Check webhook URL is correct:
   ```yaml
   exporters:
     webhook:
       url: https://your-webhook.com/vcon
   ```

3. Check authentication if needed:
   ```yaml
   exporters:
     webhook:
       auth_type: bearer
       auth_token: your_token
   ```

4. Enable DEBUG logging to see details:
   ```yaml
   logging:
     level: DEBUG
   ```

## Debugging Techniques

### Enable Debug Logging

```yaml
logging:
  level: DEBUG
  file: adapter.log
  format: text
```

### View Logs in Real-Time

```bash
tail -f adapter.log
```

### Search Logs for Errors

```bash
grep ERROR adapter.log
grep "Traceback" adapter.log
```

### Test Component Directly

Test extractor:
```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
import os

extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()
print(f"Found {len(agents)} agents")
```

Test transformer:
```python
from src.transformers.vcon_builder import VconBuilder

builder = VconBuilder()
vcon = builder.build_vcon(conversation)
print(f"vCon UUID: {vcon.uuid}")
```

Test exporter:
```python
from src.exporters.file_exporter import FileExporter

exporter = FileExporter(directory='./vcons')
exporter.export(vcon)
print("Export successful")
```

### Test with Print Statements

Add debugging output:

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')

print("Starting processing...")
vcons = adapter.process_all()
print(f"Processing complete. Created {len(vcons)} vCons")

for vcon in vcons:
    print(f"  - {vcon.uuid}")
```

## Performance Debugging

### Identify Slow Operations

```python
import time
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')

start = time.time()
vcons = adapter.process_all()
duration = time.time() - start

print(f"Total time: {duration:.2f}s")
print(f"Per vCon: {duration/len(vcons):.2f}s")
print(f"Rate: {len(vcons)/duration:.2f} vCons/s")
```

### Monitor Memory Usage

```bash
pip install memory-profiler

python3 -m memory_profiler examples/basic_usage.py
```

## Logging Best Practices

### What to Log

- Processing milestones (start, agent fetched, vcon created, etc.)
- Errors with context (which agent, which conversation)
- Configuration loaded
- Export results (successful, failed)

### Viewing Logs

```bash
# Latest entries
tail -20 adapter.log

# Real-time
tail -f adapter.log

# Search for errors
grep ERROR adapter.log

# Count by level
grep -c ERROR adapter.log
grep -c WARNING adapter.log
```

## Diagnostic Commands

### Quick Health Check

```bash
#!/bin/bash

echo "=== vCon Adapter Health Check ==="

echo "1. Checking Python..."
python3 --version

echo "2. Checking dependencies..."
python3 -c "import src; import vcon; import elevenlabs; echo 'OK'"

echo "3. Checking configuration..."
[ -f config.yml ] && echo "config.yml found" || echo "config.yml missing"

echo "4. Checking API key..."
[ -n "$ELEVENLABS_API_KEY" ] && echo "API key set" || echo "API key not set"

echo "5. Checking vcons directory..."
[ -d vcons ] && echo "vcons directory exists" || echo "vcons directory missing"

echo "=== Done ==="
```

## Resources for Help

- **Check logs**: `tail -f adapter.log`
- **Enable DEBUG**: Set `logging.level: DEBUG` in config.yml
- **Read guides**:
  - [User Guide](../02-usage/user-guide.md)
  - [Configuration](../01-getting-started/configuration.md)
  - [Testing Guide](testing-guide.md)
- **External docs**:
  - [ElevenLabs API](https://elevenlabs.io/docs/api)
  - [vCon Spec](https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon/)

---

**Still stuck? Check the logs and enable DEBUG logging for more details.**
