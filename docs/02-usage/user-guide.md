# Complete User Guide

Comprehensive guide to using the vCon ElevenLabs Adapter.

## Overview

The adapter works in three main steps:

1. **Extract**: Pull conversations from ElevenLabs API
2. **Transform**: Convert conversations to vCon format
3. **Export**: Save vCons to various backends

## Basic Usage

### Import and Initialize

```python
from src.adapter import ElevenLabsVconAdapter

# Initialize with config file
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Or with environment variables
adapter = ElevenLabsVconAdapter(
    api_key='your_key',
    export_dir='./vcons'
)
```

### Process All Conversations

```python
# Process all agents and all conversations
vcons = adapter.process_all()

for vcon in vcons:
    print(f"Created vCon: {vcon.uuid}")
```

### Process Specific Agent

```python
# Process conversations for a specific agent
agent_id = 'your_agent_id_here'
vcons = adapter.process_agent(agent_id)

print(f"Created {len(vcons)} vCons for agent {agent_id}")
```

### Process Batch of Agents

```python
# Process multiple specific agents
agent_ids = ['agent_1', 'agent_2', 'agent_3']

for agent_id in agent_ids:
    vcons = adapter.process_agent(agent_id)
    print(f"Agent {agent_id}: {len(vcons)} vCons created")
```

## Using Individual Components

### Extract Conversations

```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor

extractor = ElevenLabsExtractor(api_key='your_key')

# List all agents
agents = extractor.list_agents()
for agent in agents:
    print(f"Agent: {agent.name} (ID: {agent.id})")

# Get conversations for an agent
conversations = extractor.get_agent_conversations('agent_id')
print(f"Found {len(conversations)} conversations")

# Get audio for a conversation
audio = extractor.get_conversation_audio('conversation_id')
```

### Transform to vCon

```python
from src.transformers.party_mapper import PartyMapper
from src.transformers.dialog_processor import DialogProcessor
from src.transformers.vcon_builder import VconBuilder

# Map participants to vCon parties
mapper = PartyMapper()
parties = mapper.map_participants(conversation.participants)

# Process dialog
processor = DialogProcessor()
dialogs = processor.process_conversation(conversation)

# Build complete vCon
builder = VconBuilder()
vcon = builder.build_vcon(conversation, parties, dialogs)
```

### Export vCons

```python
from src.exporters.file_exporter import FileExporter
from src.exporters.s3_exporter import S3Exporter
from src.exporters.webhook_exporter import WebhookExporter

# File export
file_exporter = FileExporter(directory='./vcons')
file_exporter.export(vcon)

# S3 export
s3_exporter = S3Exporter(bucket='my-bucket', region='us-east-1')
s3_exporter.export(vcon)

# Webhook export
webhook_exporter = WebhookExporter(url='https://example.com/vcon')
webhook_exporter.export(vcon)
```

## Batch Processing

### Process All with File Export

```python
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Process and automatically export
vcons = adapter.process_all()

# All vCons are already exported based on config.yml settings
print(f"Total vCons created: {len(vcons)}")
```

### Export to Multiple Backends

```python
# Configure in config.yml to enable multiple exporters
# All enabled exporters will automatically export each vCon

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

# Check metrics
metrics = adapter.get_metrics()
print(f"Total files exported: {metrics.get('exports_total')}")
```

### Selective Exporting

```python
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Process without automatic export
vcons = adapter.process_all()

# Export specific vCons manually
for vcon in vcons:
    # Only export to file
    adapter.exporters['file'].export(vcon)
    
    # Or only to S3 if needed
    if should_export_to_s3(vcon):
        adapter.exporters['s3'].export(vcon)
```

## Advanced Usage

### Custom Configuration

```python
from src.config import Config

config_dict = {
    'elevenlabs': {
        'api_key': 'your_key',
        'agent_ids': ['agent_1', 'agent_2'],
        'timeout': 60
    },
    'exporters': {
        'file': {
            'enabled': True,
            'directory': './output'
        },
        's3': {
            'enabled': True,
            'bucket': 'my-bucket'
        }
    },
    'logging': {
        'level': 'DEBUG',
        'file': 'app.log'
    }
}

config = Config(**config_dict)
adapter = ElevenLabsVconAdapter(config=config)
vcons = adapter.process_all()
```

### Error Handling

```python
try:
    vcons = adapter.process_all()
except Exception as e:
    print(f"Error processing vCons: {e}")
    # Check adapter.log for details
```

### Access Metrics

```python
# Get processing metrics
metrics = adapter.get_metrics()

print(f"Agents processed: {metrics.get('agents_processed')}")
print(f"Conversations found: {metrics.get('conversations_found')}")
print(f"vCons created: {metrics.get('vcons_created')}")
print(f"Exports successful: {metrics.get('exports_successful')}")
print(f"Errors encountered: {metrics.get('errors')}")
```

## Configuration File Method (Recommended)

### Setup with config.yml

```yaml
# config.yml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  agent_ids: all
  poll_interval: 300

exporters:
  file:
    enabled: true
    directory: ./vcons
  
  s3:
    enabled: true
    bucket: my-bucket
    region: us-east-1

logging:
  level: INFO
  file: adapter.log
```

### Use in Code

```python
from src.adapter import ElevenLabsVconAdapter

# Initialize with config file
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Process all
vcons = adapter.process_all()

# Check results
print(f"Created {len(vcons)} vCons")
```

## Environment Variables

Use environment variables for sensitive data:

```bash
# Set environment variables
export ELEVENLABS_API_KEY="your_key"
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
```

Then reference in config.yml:

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
```

## Best Practices

### 1. Use Configuration Files

Prefer config files over hardcoding:

```python
# Good
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Avoid
adapter = ElevenLabsVconAdapter(api_key='key_hardcoded_here')
```

### 2. Enable Debug Logging

For troubleshooting, enable DEBUG logging:

```yaml
logging:
  level: DEBUG  # Change from INFO
```

### 3. Handle Errors Gracefully

```python
try:
    vcons = adapter.process_all()
except Exception as e:
    logger.error(f"Processing failed: {e}")
    # Implement retry logic or notifications
```

### 4. Check Metrics

Monitor processing metrics:

```python
metrics = adapter.get_metrics()
if metrics.get('errors'):
    print(f"Errors encountered: {metrics['errors']}")
```

### 5. Use Batch Processing

For large numbers of conversations, process in batches:

```python
batch_size = 10
all_agents = extractor.list_agents()

for i in range(0, len(all_agents), batch_size):
    batch = all_agents[i:i+batch_size]
    for agent in batch:
        adapter.process_agent(agent.id)
```

## Troubleshooting

### No vCons Created

1. Check `adapter.log` for errors
2. Verify API key is correct
3. Ensure agent has conversations
4. Check network connectivity

### vCons Not Exported

1. Verify exporter is enabled in config
2. Check exporter permissions (file directory, S3 bucket, webhook access)
3. Review logs for export errors

### API Connection Issues

1. Test connection manually:
   ```python
   from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
   extractor = ElevenLabsExtractor(api_key='your_key')
   agents = extractor.list_agents()
   ```

2. Check network and firewall
3. Verify API key hasn't expired

## See Also

- **[API Reference](api-reference.md)** - Complete API documentation
- **[Examples](examples.md)** - Code examples for common tasks
- **[Configuration](../01-getting-started/configuration.md)** - Configuration reference
- **[Testing Guide](../03-testing/testing-guide.md)** - Running tests
