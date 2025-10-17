# API Reference

Complete reference for the vCon ElevenLabs Adapter API.

## Main Adapter

### `ElevenLabsVconAdapter`

Main orchestrator class for the adapter.

#### Constructor

```python
ElevenLabsVconAdapter(config_file: str = None, config: Config = None, **kwargs)
```

**Parameters:**
- `config_file` (str, optional): Path to YAML configuration file
- `config` (Config, optional): Configuration object
- `**kwargs`: Additional configuration parameters

**Example:**
```python
adapter = ElevenLabsVconAdapter(config_file='config.yml')
```

#### Methods

##### `process_all() -> List[Vcon]`

Process all agents and their conversations.

```python
vcons = adapter.process_all()
```

**Returns:** List of created vCon objects

---

##### `process_agent(agent_id: str) -> List[Vcon]`

Process conversations for a specific agent.

```python
vcons = adapter.process_agent('agent_id_123')
```

**Parameters:**
- `agent_id` (str): ElevenLabs agent ID

**Returns:** List of created vCons for the agent

---

##### `get_metrics() -> Dict`

Get processing metrics and statistics.

```python
metrics = adapter.get_metrics()
```

**Returns:** Dictionary with metrics:
- `agents_processed`: Number of agents processed
- `conversations_found`: Total conversations found
- `vcons_created`: Number of vCons created
- `exports_successful`: Successful exports
- `processing_time`: Total processing time in seconds
- `errors`: Number of errors encountered

## Extractors

### `ElevenLabsExtractor`

Extracts data from ElevenLabs API.

#### Constructor

```python
ElevenLabsExtractor(api_key: str, timeout: int = 30, max_retries: int = 3)
```

**Parameters:**
- `api_key` (str): ElevenLabs API key
- `timeout` (int): Request timeout in seconds (default: 30)
- `max_retries` (int): Maximum retry attempts (default: 3)

#### Methods

##### `list_agents() -> List[Agent]`

Get all agents.

```python
agents = extractor.list_agents()
```

**Returns:** List of Agent objects

---

##### `get_agent_conversations(agent_id: str) -> List[Conversation]`

Get conversations for an agent.

```python
conversations = extractor.get_agent_conversations('agent_id')
```

**Parameters:**
- `agent_id` (str): Agent ID

**Returns:** List of Conversation objects

---

##### `get_conversation_audio(conversation_id: str) -> bytes`

Get audio for a conversation.

```python
audio_data = extractor.get_conversation_audio('conv_id')
```

**Parameters:**
- `conversation_id` (str): Conversation ID

**Returns:** Audio bytes

## Transformers

### `PartyMapper`

Maps participants to vCon Party objects.

```python
from src.transformers.party_mapper import PartyMapper

mapper = PartyMapper()
parties = mapper.map_participants(participants)
```

---

### `DialogProcessor`

Processes conversations into vCon Dialog objects.

```python
from src.transformers.dialog_processor import DialogProcessor

processor = DialogProcessor()
dialogs = processor.process_conversation(conversation)
```

---

### `VconBuilder`

Assembles complete vCon objects.

```python
from src.transformers.vcon_builder import VconBuilder

builder = VconBuilder()
vcon = builder.build_vcon(conversation, parties, dialogs)
```

## Exporters

### `FileExporter`

Exports vCons to local filesystem.

#### Constructor

```python
FileExporter(directory: str = './vcons', overwrite: bool = False)
```

**Parameters:**
- `directory` (str): Output directory
- `overwrite` (bool): Overwrite existing files

#### Methods

##### `export(vcon: Vcon) -> None`

Export a vCon to file.

```python
file_exporter = FileExporter(directory='./vcons')
file_exporter.export(vcon)
```

---

### `S3Exporter`

Exports vCons to AWS S3.

#### Constructor

```python
S3Exporter(
    bucket: str,
    region: str = 'us-east-1',
    prefix: str = '',
    encryption: str = 'AES256',
    kms_key_id: str = None
)
```

**Parameters:**
- `bucket` (str): S3 bucket name
- `region` (str): AWS region
- `prefix` (str): Path prefix in bucket
- `encryption` (str): 'AES256' or 'KMS'
- `kms_key_id` (str): KMS key ARN (required if encryption='KMS')

#### Methods

##### `export(vcon: Vcon) -> None`

Export a vCon to S3.

```python
s3_exporter = S3Exporter(bucket='my-bucket')
s3_exporter.export(vcon)
```

---

### `WebhookExporter`

Exports vCons via HTTP webhook.

#### Constructor

```python
WebhookExporter(
    url: str,
    auth_type: str = None,
    auth_token: str = None,
    retry_attempts: int = 3,
    retry_delay: float = 1.0,
    timeout: int = 30
)
```

**Parameters:**
- `url` (str): Webhook endpoint URL
- `auth_type` (str): 'bearer' or 'api_key' (optional)
- `auth_token` (str): Authentication token
- `retry_attempts` (int): Number of retries
- `retry_delay` (float): Delay between retries (seconds)
- `timeout` (int): Request timeout (seconds)

#### Methods

##### `export(vcon: Vcon) -> None`

Export a vCon via webhook.

```python
webhook = WebhookExporter(url='https://example.com/vcon')
webhook.export(vcon)
```

## Models

### `Agent`

Represents an ElevenLabs agent.

**Attributes:**
- `id` (str): Agent ID
- `name` (str): Agent name
- `status` (str): Agent status
- `created_at` (datetime, optional): Creation timestamp

### `Conversation`

Represents a conversation.

**Attributes:**
- `id` (str): Conversation ID
- `agent_id` (str): Associated agent ID
- `start_time` (datetime): Conversation start time
- `status` (str): Conversation status
- `participants` (List[ConversationParticipant]): Participants
- `transcripts` (List[Transcript], optional): Transcripts
- `audio` (AudioRecording, optional): Audio recording

### `ConversationParticipant`

Represents a conversation participant.

**Attributes:**
- `id` (str): Participant ID
- `name` (str): Participant name
- `role` (str): Role (e.g., 'agent', 'customer')
- `email` (str, optional): Email address

### `AudioRecording`

Represents audio for a conversation.

**Attributes:**
- `url` (str): Audio URL
- `mime_type` (str): MIME type
- `duration` (int, optional): Duration in milliseconds

### `Transcript`

Represents a transcript.

**Attributes:**
- `text` (str): Transcript text
- `language` (str): Language code
- `confidence` (float, optional): Confidence score

## Configuration

See [Configuration Reference](../01-getting-started/configuration.md) for complete configuration options.

### Config Class

```python
from src.config import Config

config = Config(**config_dict)
```

**Main sections:**
- `elevenlabs`: ElevenLabs settings
- `exporters`: Export backend configuration
- `logging`: Logging configuration
- `vcon`: vCon generation options

## Exceptions

### Common Exceptions

```python
try:
    adapter.process_all()
except FileNotFoundError:
    # Configuration file not found
except Exception as e:
    # General error
```

Check `adapter.log` for detailed error information.

## Logging

Access logs:

```python
# View in real-time
tail -f adapter.log

# Search for errors
grep ERROR adapter.log
```

Enable DEBUG logging in config.yml:

```yaml
logging:
  level: DEBUG  # More detailed output
```

## Examples

See [Code Examples](examples.md) for practical usage patterns.

---

For more information:
- [User Guide](user-guide.md)
- [Examples](examples.md)
- [Configuration](../01-getting-started/configuration.md)
