# vCon ElevenLabs Adapter

Convert ElevenLabs agent interactions to standardized vCon (Virtualized Conversation) format and export to multiple backends.

## Features

- Extract conversation data from ElevenLabs.io API
- Transform conversations into standardized vCon format
- Export vCons to multiple backends:
  - Local filesystem
  - AWS S3 bucket
  - HTTP webhook endpoints
- Batch processing support
- Comprehensive logging and error handling
- Privacy-focused design with support for PII handling
- Configurable via YAML with environment variable substitution

## Installation

### Prerequisites

- Python 3.12+ (required by vcon 1.x)
- pip or conda
- ElevenLabs API key
- (Optional) AWS credentials for S3 export
- (Optional) Webhook endpoint for real-time notifications

### Setup

```bash
git clone https://github.com/yourusername/vcon-eleven-labs-adapter.git
cd vcon-eleven-labs-adapter
pip install -r requirements.txt
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your ElevenLabs API key and other settings.

### 2. Configure Pipeline

Create `config.yml` from the example:

```bash
cp config.yml.example config.yml
```

Edit to enable/disable exporters and set options.

### 3. Run Adapter

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()

for vcon in vcons:
    print(f"Created vCon: {vcon.uuid}")
```

## Configuration

### Environment Variables

```bash
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_AGENT_IDS=agent_1,agent_2
EXPORT_DIR=./vcons
AWS_S3_BUCKET=my-bucket
WEBHOOK_URL=https://example.com/webhook
LOG_LEVEL=INFO
```

### YAML Configuration

See `config.yml.example` for full options. Key sections:

#### ElevenLabs Settings
```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  agent_ids: all
  poll_interval: 300
  batch_size: 10
```

#### File Export
```yaml
exporters:
  file:
    enabled: true
    directory: ./vcons
```

#### S3 Export
```yaml
exporters:
  s3:
    enabled: true
    bucket: my-bucket
    region: us-east-1
    prefix: elevenlabs/
```

#### Webhook Export
```yaml
exporters:
  webhook:
    enabled: true
    url: https://example.com/vcon-receiver
    batch_size: 10
    retry_attempts: 3
```

## Usage Examples

### Basic Usage

```python
from src.adapter import ElevenLabsVconAdapter

adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_all()
```

### Process Single Agent

```python
adapter = ElevenLabsVconAdapter(config_file='config.yml')
vcons = adapter.process_agent('agent_id_123')
```

### Batch Processing

```python
adapter = ElevenLabsVconAdapter(config_file='config.yml')
agent_ids = ['agent_1', 'agent_2', 'agent_3']

for agent_id in agent_ids:
    vcons = adapter.process_agent(agent_id)
    print(f"Processed {len(vcons)} conversations for {agent_id}")
```

### Export to Specific Backend

```python
vcon = adapter.process_agent('agent_123')[0]

adapter.exporters['file'].export(vcon)
adapter.exporters['s3'].export(vcon)
adapter.exporters['webhook'].export(vcon)
```

## vCon Structure

Generated vCons follow draft-ietf-vcon-vcon-core-05 (`"vcon": "0.5.0"`), built
with `vcon>=1.0.3,<2`. Version 1.0.0 of this adapter moved from the 0.4.0 shape
to 0.5.0; consumers that only understand 0.4.0 must be upgraded (vcon-lib 1.x
reads both). Each generated vCon contains:

- **Parties**: Agent and customer information
- **Sessions**: one Session per ElevenLabs conversation (start, duration, and
  the participants as its `parties`); every Dialog is listed in it
- **Dialog**: the audio recording (`type: "recording"`, only when there is
  audio: a `url` with a sha512 `content_hash` when the adapter downloaded the
  file, or an unpadded base64url `body`) and the transcript text
  (`type: "text"`); Dialog `parties` are the contributors
- **Analysis**: Optional transcripts, summaries (if available from ElevenLabs),
  `vendor: "elevenlabs"`, `encoding: "json"` with the JSON value as `body`,
  pointing at the recording (or the transcript Dialog when there is no audio)
- **Attachments**: `call_record` conversation metadata (`encoding: "json"`)
  and `tags`, scoped with `party` plus `session`
- **Metadata**: UUID, `created_at`, source tags

A conversation without audio no longer gets a placeholder recording Dialog;
its start and duration are on the Session.

## Architecture

```
ElevenLabs API
    |
    v
ElevenLabsExtractor (extracts raw data)
    |
    v
PartyMapper (participant data)
    |
    v
DialogProcessor (conversation content)
    |
    v
VconBuilder (assemble complete vCon)
    |
    +----> FileExporter
    +----> S3Exporter
    +----> WebhookExporter
```

## Error Handling

The adapter includes comprehensive error handling:

- Automatic retry on API rate limits
- Graceful degradation for missing optional fields
- Detailed error logging
- Continuation on non-fatal errors

## Logging

Logging is configured in `config.yml`:

```yaml
logging:
  level: INFO
  file: adapter.log
  console: true
  format: json
```

View logs:
```bash
tail -f adapter.log
```

## Testing

Run tests:

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Development

### Project Structure

```
src/
  adapter.py                 # Main adapter class
  config.py                  # Configuration management
  logger.py                  # Logging setup
  extractors/
    elevenlabs_extractor.py  # ElevenLabs API client
  transformers/
    party_mapper.py          # Participant mapping
    dialog_processor.py      # Conversation processing
    vcon_builder.py          # vCon assembly
  exporters/
    file_exporter.py         # Filesystem export
    s3_exporter.py           # S3 export
    webhook_exporter.py      # Webhook export
  models/
    elevenlabs_models.py     # Data models
```

### Contributing

1. Create a feature branch
2. Make changes
3. Add tests
4. Ensure all tests pass
5. Submit pull request

## Privacy & Security

- PII is handled carefully; consider vCon encryption for sensitive data
- API keys should be stored in environment variables, never committed to version control
- S3 exports support encryption options (SSE-S3, SSE-KMS)
- Webhook exports should use HTTPS with proper authentication

## Troubleshooting

### ElevenLabs API Connection Issues

Check your API key and internet connection:

```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
extractor = ElevenLabsExtractor(api_key='your_key')
agents = extractor.list_agents()
```

### S3 Upload Failures

Verify AWS credentials and bucket permissions:

```bash
aws s3 ls s3://your-bucket/
```

### Webhook Delivery Issues

Check webhook logs and verify endpoint is accessible:

```bash
curl -X POST https://your-webhook-url -H "Content-Type: application/json" -d '{}'
```

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

## References

- [vCon Specification](https://datatracker.ietf.org/doc/draft-ietf-vcon-vcon/)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs/api)
- [vCon Python Library](https://github.com/py-vcon/py-vcon)
