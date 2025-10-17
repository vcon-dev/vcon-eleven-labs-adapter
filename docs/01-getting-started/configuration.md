# Configuration Reference

Complete guide to configuring the vCon ElevenLabs Adapter.

## Configuration File Location

The adapter uses a YAML configuration file:

```bash
# Default location
config.yml

# Custom location (specify when creating adapter)
config_file='custom/path/config.yml'
```

## Environment Variables

Configuration supports environment variable substitution using `${VARIABLE_NAME}` syntax:

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}  # Replaced with value of ELEVENLABS_API_KEY env var
```

Set environment variables:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
```

## ElevenLabs Configuration

### Required Settings

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}  # Your ElevenLabs API key
  agent_ids: all                   # Process all agents
  # OR specify specific agents:
  # agent_ids:
  #   - agent_id_1
  #   - agent_id_2
```

### Optional Settings

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  agent_ids: all
  poll_interval: 300              # Check for new conversations every 300 seconds (5 min)
  batch_size: 10                  # Fetch 10 conversations per API call
  timeout: 30                     # Request timeout in seconds (increase if slow network)
  max_retries: 3                  # Maximum retry attempts for API calls
```

## Exporters Configuration

### File Exporter

Export vCons to local filesystem:

```yaml
exporters:
  file:
    enabled: true
    directory: ./vcons              # Directory to save vCon files
    overwrite: false                # Don't overwrite existing files
    # Optional: template for filenames
    # filename_template: "vcon_{uuid}.json"
```

### S3 Exporter

Export vCons to AWS S3:

```yaml
exporters:
  s3:
    enabled: false                  # Set to true to use
    bucket: my-vcon-bucket          # S3 bucket name
    region: us-east-1               # AWS region
    prefix: elevenlabs/             # Path prefix in bucket
    # Optional: encryption
    # encryption: AES256             # or KMS for server-side encryption
    # kms_key_id: arn:aws:kms:...   # Required if encryption: KMS
    # Optional: custom metadata
    # metadata:
    #   environment: production
    #   team: vcon-team
```

**AWS Credentials:**

Set AWS credentials as environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-east-1"
```

Or use AWS CLI configuration:

```bash
aws configure
```

### Webhook Exporter

POST vCons to HTTP webhooks:

```yaml
exporters:
  webhook:
    enabled: false                  # Set to true to use
    url: https://example.com/vcon   # Webhook endpoint URL
    # Optional: authentication
    # auth_type: bearer              # or api_key
    # auth_token: your_token_here    # Bearer token or API key value
    # Optional: batch processing
    # batch_size: 5                  # Send up to 5 vCons per request
    # Optional: retry settings
    # retry_attempts: 3              # Number of retry attempts
    # retry_delay: 1                 # Delay between retries (seconds)
    # Optional: timeout
    # timeout: 30                    # Request timeout in seconds
    # Optional: verify SSL
    # verify_ssl: true               # Set to false to disable SSL verification (not recommended)
```

### Enable Multiple Exporters

You can enable multiple exporters simultaneously:

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

## Logging Configuration

### Log Levels

```yaml
logging:
  level: INFO                      # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: adapter.log                # Log file path
  console: true                    # Also log to console
  format: text                     # text or json
  # Optional: max file size
  # max_bytes: 10485760           # 10 MB
  # Optional: backup count
  # backup_count: 5               # Keep 5 backup files
```

### Log Levels Explained

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for problems
- **CRITICAL**: Critical errors requiring immediate attention

### Log Format

#### Text Format (Human-Readable)

```
2025-10-17 15:00:01 INFO: Processing all agents
2025-10-17 15:00:02 INFO: Successfully created 2 vCons
```

#### JSON Format (Machine-Readable)

```json
{"timestamp": "2025-10-17T15:00:01", "level": "INFO", "message": "Processing all agents"}
```

## vCon Generation Options

```yaml
vcon:
  # Optional: include analysis data if available
  include_analysis: true
  
  # Optional: include attachments
  include_attachments: true
  
  # Optional: custom subject pattern
  subject_template: "Call from {agent_name}"
```

## Complete Example Configuration

```yaml
# ElevenLabs Configuration
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  agent_ids: all
  poll_interval: 300
  batch_size: 10
  timeout: 30

# Exporters Configuration
exporters:
  file:
    enabled: true
    directory: ./vcons
    overwrite: false
  
  s3:
    enabled: false
    bucket: my-vcon-bucket
    region: us-east-1
    prefix: elevenlabs/
    encryption: AES256
  
  webhook:
    enabled: false
    url: https://example.com/vcon
    auth_type: bearer
    auth_token: ${WEBHOOK_TOKEN}

# Logging Configuration
logging:
  level: INFO
  file: adapter.log
  console: true
  format: text

# vCon Options
vcon:
  include_analysis: true
  include_attachments: true
```

## Configuration File Example

Start with the provided example:

```bash
cp config.yml.example config.yml
```

Then edit `config.yml` with your specific settings.

## Dynamic Configuration

You can also configure the adapter programmatically:

```python
from src.adapter import ElevenLabsVconAdapter
from src.config import Config

# Create configuration
config = Config(
    elevenlabs={
        'api_key': 'your_key',
        'agent_ids': 'all'
    },
    exporters={
        'file': {'enabled': True, 'directory': './vcons'}
    }
)

# Create adapter with config
adapter = ElevenLabsVconAdapter(config=config)
vcons = adapter.process_all()
```

## Troubleshooting Configuration

### "No such file or directory: config.yml"

**Solution**: Create config.yml from example:
```bash
cp config.yml.example config.yml
```

### "Invalid API key"

**Solution**: Verify API key:
1. Go to https://elevenlabs.io/app/settings/api-keys
2. Copy your API key exactly (no extra spaces)
3. Set in config.yml or environment variable

### "YAML parsing error"

**Solution**: Check YAML syntax:
- Use 2 spaces for indentation (not tabs)
- Ensure colons are followed by spaces
- Quote strings with special characters

### "Connection refused"

**Solution**: Check network and timeout:
```yaml
elevenlabs:
  timeout: 60  # Increase from default 30
```

---

**See Also:**
- [Quick Start](quickstart.md)
- [User Guide](../02-usage/user-guide.md)
- [ElevenLabs API Docs](https://elevenlabs.io/docs/api)
