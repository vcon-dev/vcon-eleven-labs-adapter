# Code Examples

Practical examples for common use cases with the vCon ElevenLabs Adapter.

## Example 1: Basic Usage

Process all conversations and export to local files:

```python
from src.adapter import ElevenLabsVconAdapter

# Initialize adapter
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Process all agents and conversations
vcons = adapter.process_all()

# Print results
print(f"Successfully created {len(vcons)} vCons")
for vcon in vcons:
    print(f"  UUID: {vcon.uuid}")
```

## Example 2: Process Specific Agent

Process conversations for a specific ElevenLabs agent:

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Process a specific agent
agent_id = "agent_5301k7573nhxeyztfjbyavk7c8ts"
vcons = adapter.process_agent(agent_id)

print(f"Agent {agent_id}: {len(vcons)} vCons created")
```

## Example 3: List Agents and Select

Interactively select an agent to process:

```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
from src.adapter import ElevenLabsVconAdapter
import os

# Get API key
api_key = os.getenv('ELEVENLABS_API_KEY')
extractor = ElevenLabsExtractor(api_key=api_key)

# List all agents
agents = extractor.list_agents()

print("Available Agents:")
for i, agent in enumerate(agents):
    print(f"{i+1}. {agent.name} (ID: {agent.id})")

# Get user selection
choice = int(input("Select agent (number): ")) - 1
selected_agent = agents[choice]

# Process selected agent
adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_agent(selected_agent.id)

print(f"Processed {len(vcons)} conversations from {selected_agent.name}")
```

## Example 4: Export to Different Backends

Export vCons to multiple backends:

```python
from src.adapter import ElevenLabsVconAdapter
from src.exporters.file_exporter import FileExporter
from src.exporters.s3_exporter import S3Exporter

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

# Export to local files
file_exporter = FileExporter(directory='./vcons')
for vcon in vcons:
    file_exporter.export(vcon)
    print(f"Exported to file: {vcon.uuid}")

# Export to S3
s3_exporter = S3Exporter(bucket='my-bucket', region='us-east-1')
for vcon in vcons:
    s3_exporter.export(vcon)
    print(f"Exported to S3: {vcon.uuid}")
```

## Example 5: Error Handling

Handle errors gracefully:

```python
from src.adapter import ElevenLabsVconAdapter
import logging

logger = logging.getLogger(__name__)

try:
    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()
    print(f"Successfully processed {len(vcons)} vCons")
    
except FileNotFoundError as e:
    logger.error(f"Configuration file not found: {e}")
    
except Exception as e:
    logger.error(f"Error processing vCons: {e}")
    # Check adapter.log for details
```

## Example 6: Process with Custom Configuration

Use programmatic configuration instead of YAML:

```python
from src.adapter import ElevenLabsVconAdapter
from src.config import Config

# Create configuration dictionary
config_dict = {
    'elevenlabs': {
        'api_key': 'your_api_key',
        'agent_ids': ['agent_1', 'agent_2'],
        'batch_size': 5,
        'timeout': 60
    },
    'exporters': {
        'file': {
            'enabled': True,
            'directory': './vcons'
        },
        'webhook': {
            'enabled': False  # Disabled for now
        }
    },
    'logging': {
        'level': 'INFO',
        'file': 'processing.log'
    }
}

# Create config object
config = Config(**config_dict)

# Initialize adapter with config
adapter = ElevenLabsVconAdapter(config=config)
vcons = adapter.process_all()

print(f"Processed {len(vcons)} vCons with custom configuration")
```

## Example 7: Check Processing Metrics

Monitor processing metrics:

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

# Get metrics
metrics = adapter.get_metrics()

print("Processing Metrics:")
print(f"  Agents processed: {metrics.get('agents_processed', 0)}")
print(f"  Conversations found: {metrics.get('conversations_found', 0)}")
print(f"  vCons created: {metrics.get('vcons_created', 0)}")
print(f"  Exports successful: {metrics.get('exports_successful', 0)}")
print(f"  Processing time: {metrics.get('processing_time', 0):.2f}s")

if metrics.get('errors'):
    print(f"  Errors: {metrics['errors']}")
```

## Example 8: Process in Batches

Process large numbers of conversations in batches:

```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
from src.adapter import ElevenLabsVconAdapter
import os

api_key = os.getenv('ELEVENLABS_API_KEY')
extractor = ElevenLabsExtractor(api_key=api_key)
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Get all agents
all_agents = extractor.list_agents()

# Process in batches
batch_size = 5
total_vcons = 0

for i in range(0, len(all_agents), batch_size):
    batch = all_agents[i:i+batch_size]
    print(f"\nProcessing batch {i//batch_size + 1}...")
    
    for agent in batch:
        vcons = adapter.process_agent(agent.id)
        total_vcons += len(vcons)
        print(f"  {agent.name}: {len(vcons)} vCons")

print(f"\nTotal vCons processed: {total_vcons}")
```

## Example 9: Direct Component Usage

Use adapter components individually:

```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
from src.transformers.vcon_builder import VconBuilder
from src.exporters.file_exporter import FileExporter
import os

# Extract
extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()
conversations = extractor.get_agent_conversations(agents[0].id)

# Transform
builder = VconBuilder()
vcons = []
for conversation in conversations:
    vcon = builder.build_vcon(conversation)
    vcons.append(vcon)

# Export
exporter = FileExporter(directory='./vcons')
for vcon in vcons:
    exporter.export(vcon)

print(f"Processed {len(vcons)} vCons using individual components")
```

## Example 10: Filter and Process

Filter conversations before processing:

```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
from src.adapter import ElevenLabsVconAdapter
from datetime import datetime, timedelta
import os

# Get conversations
extractor = ElevenLabsExtractor(api_key=os.getenv('ELEVENLABS_API_KEY'))
agents = extractor.list_agents()
all_conversations = extractor.get_agent_conversations(agents[0].id)

# Filter: only conversations from last 24 hours
cutoff_time = datetime.now() - timedelta(days=1)
filtered_conversations = [
    conv for conv in all_conversations
    if conv.start_time >= cutoff_time
]

print(f"Found {len(filtered_conversations)} conversations in last 24 hours")

# Process filtered conversations
adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

print(f"Created {len(vcons)} vCons from filtered conversations")
```

## Example 11: Schedule Regular Processing

Run adapter periodically with APScheduler:

```python
from src.adapter import ElevenLabsVconAdapter
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def process_vcons():
    """Process vCons on a schedule"""
    try:
        adapter = ElevenLabsVconAdapter(config_file='config.yml')
        vcons = adapter.process_all()
        logger.info(f"Scheduled processing: {len(vcons)} vCons created")
    except Exception as e:
        logger.error(f"Scheduled processing failed: {e}")

# Schedule to run every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(process_vcons, 'interval', minutes=5)
scheduler.start()

print("Scheduler started. Processing vCons every 5 minutes...")

# Keep running
try:
    while True:
        pass
except KeyboardInterrupt:
    scheduler.shutdown()
```

## Example 12: Webhook Export with Retry

Export to webhook with automatic retry:

```python
from src.adapter import ElevenLabsVconAdapter
from src.exporters.webhook_exporter import WebhookExporter
import time

config_file = 'config.yml'
adapter = ElevenLabsVconAdapter(config_file=config_file)
vcons = adapter.process_all()

# Create webhook exporter
webhook = WebhookExporter(
    url='https://example.com/vcon-receiver',
    auth_type='bearer',
    auth_token='your_token',
    retry_attempts=3,
    retry_delay=2
)

# Export with retry
for vcon in vcons:
    try:
        webhook.export(vcon)
        print(f"Exported {vcon.uuid} to webhook")
    except Exception as e:
        print(f"Failed to export {vcon.uuid}: {e}")
        # Will retry automatically based on config
```

## Example 13: S3 Export with Encryption

Export to AWS S3 with encryption:

```python
from src.adapter import ElevenLabsVconAdapter
from src.exporters.s3_exporter import S3Exporter

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

# Create S3 exporter with KMS encryption
s3_exporter = S3Exporter(
    bucket='my-secure-bucket',
    region='us-east-1',
    prefix='vcons/secured/',
    encryption='KMS',
    kms_key_id='arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789012'
)

# Export all vCons
for vcon in vcons:
    s3_exporter.export(vcon)
    print(f"Encrypted and exported {vcon.uuid} to S3")
```

---

For more information, see:
- [User Guide](user-guide.md)
- [API Reference](api-reference.md)
- [Configuration](../01-getting-started/configuration.md)

## AI Integration Examples

### Export to OpenAI

```python
from src.exporters.openai_exporter import OpenAIExporter

# Initialize exporter
exporter = OpenAIExporter(api_key="sk-...")

# Export single vCon
result = exporter.export(vcon)
print(f"File ID: {result['file_id']}")

# Export batch
results = exporter.export_batch(vcons)

# List files
files = exporter.list_files(purpose="assistants")

# Delete file
exporter.delete_file(file_id)
```

### Export to Anthropic

```python
from src.exporters.anthropic_exporter import AnthropicExporter

# Initialize exporter
exporter = AnthropicExporter(api_key="sk-ant-...")

# Export single vCon
result = exporter.export(vcon)
print(f"File ID: {result['file_id']}")

# Export batch
results = exporter.export_batch(vcons)

# Create RAG context
context = exporter.create_retrieval_context(
    file_ids=[result['file_id']],
    query="Analyze this conversation"
)
```

For more AI integration examples, see [AI Integrations](ai-integrations.md).
