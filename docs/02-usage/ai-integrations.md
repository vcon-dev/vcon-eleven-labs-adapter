# AI Integrations - OpenAI & Anthropic

Export vCons directly to OpenAI and Anthropic for use with their AI models.

## Overview

The adapter now supports exporting vCons to:
- **OpenAI Files API** - For use with assistants, RAG, and fine-tuning
- **Anthropic Files API** - For use with Claude and retrieval features

## OpenAI Integration

### Installation

```bash
pip install openai>=1.0.0
```

### Configuration

Add to `config.yml`:

```yaml
exporters:
  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY}
    organization: ${OPENAI_ORG_ID}  # Optional
    purpose: "assistants"            # assistants, batch, fine-tune, or vision
```

### Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Optional
```

### Usage

#### Basic Export

```python
from src.exporters.openai_exporter import OpenAIExporter

exporter = OpenAIExporter(api_key="sk-...")
result = exporter.export(vcon)

print(f"File uploaded: {result['file_id']}")
```

#### List Files

```python
files = exporter.list_files(purpose="assistants")
for file in files:
    print(f"File: {file.filename}, ID: {file.id}")
```

#### Delete File

```python
exporter.delete_file(file_id)
```

#### Batch Export

```python
results = exporter.export_batch(vcons)
for result in results:
    if 'error' not in result:
        print(f"Uploaded: {result['file_id']}")
```

#### Use with Assistants

```python
from openai import OpenAI

client = OpenAI()

# Upload vCon with vCon exporter
exporter = OpenAIExporter()
result = exporter.export(vcon)
file_id = result['file_id']

# Create assistant with uploaded file
assistant = client.beta.assistants.create(
    name="Conversation Analyzer",
    model="gpt-4",
    tools=[{"type": "retrieval"}],
    file_ids=[file_id]
)

# Use with threads
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyze this conversation"
)
```

## Anthropic Integration

### Installation

```bash
pip install anthropic>=0.7.0
```

### Configuration

Add to `config.yml`:

```yaml
exporters:
  anthropic:
    enabled: true
    api_key: ${ANTHROPIC_API_KEY}
    timeout: 30
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Usage

#### Basic Export

```python
from src.exporters.anthropic_exporter import AnthropicExporter

exporter = AnthropicExporter(api_key="sk-ant-...")
result = exporter.export(vcon)

print(f"File uploaded: {result['file_id']}")
```

#### List Files

```python
files = exporter.list_files(limit=100)
for file in files:
    print(f"File: {file.filename}, ID: {file.id}")
```

#### Delete File

```python
exporter.delete_file(file_id)
```

#### Batch Export

```python
results = exporter.export_batch(vcons)
for result in results:
    if 'error' not in result:
        print(f"Uploaded: {result['file_id']}")
```

#### Use with Claude (RAG)

```python
from anthropic import Anthropic

client = Anthropic()

# Upload vCon
exporter = AnthropicExporter()
result = exporter.export(vcon)
file_id = result['file_id']

# Create retrieval context
context = exporter.create_retrieval_context(
    file_ids=[file_id],
    query="Analyze this conversation"
)

# Use with Claude
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    system="You are a conversation analyst.",
    messages=[
        {
            "role": "user",
            "content": f"Analyze this conversation context: {context}"
        }
    ]
)
```

## Configuration Example

Complete configuration with all exporters:

```yaml
elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  agent_ids: all

exporters:
  file:
    enabled: true
    directory: ./vcons

  s3:
    enabled: false
    bucket: my-bucket

  webhook:
    enabled: false
    url: https://example.com/webhook

  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY}
    purpose: "assistants"

  anthropic:
    enabled: true
    api_key: ${ANTHROPIC_API_KEY}

logging:
  level: INFO
  file: adapter.log
```

## Complete Example

Process conversations and export to all platforms:

```python
from src.adapter import ElevenLabsVconAdapter

# Configure adapter
adapter = ElevenLabsVconAdapter(config_file='config.yml')

# Process all conversations
vcons = adapter.process_all()

print(f"Processed {len(vcons)} conversations")

# Exporters automatically handle exports based on config
# Files go to: local files, S3, OpenAI, and Anthropic

# Access individual exporters for more control
openai_exporter = adapter.exporters['openai']
anthropic_exporter = adapter.exporters['anthropic']

# List uploaded files
openai_files = openai_exporter.list_files()
print(f"OpenAI files: {len(list(openai_files))}")

anthropic_files = anthropic_exporter.list_files()
print(f"Anthropic files: {len(list(anthropic_files))}")
```

## Use Cases

### With OpenAI

1. **Assistants** - Create AI assistants that can analyze conversations
2. **RAG** - Retrieve conversation context for question answering
3. **Fine-tuning** - Use conversations as training data
4. **Vision** - Process conversation transcripts

### With Anthropic

1. **Claude Integration** - Use Claude to analyze conversations
2. **Document Retrieval** - Ask Claude questions about conversation content
3. **Multi-turn Analysis** - Have Claude analyze conversations across multiple turns
4. **Content Classification** - Classify conversations by type or sentiment

## Error Handling

```python
try:
    result = exporter.export(vcon)
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install openai")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Export failed: {e}")
```

## Troubleshooting

### "openai package required"

```bash
pip install openai>=1.0.0
```

### "anthropic package required"

```bash
pip install anthropic>=0.7.0
```

### "API key required"

Ensure environment variables are set:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Files Not Uploading

1. Check API keys are valid
2. Verify internet connection
3. Enable DEBUG logging for details
4. Check service status

## Limits & Best Practices

### OpenAI Files API

- Max file size: 512 MB
- File retention: 30 days (unless used in assistant)
- Supported formats: JSON, PDF, TXT, DOCX, etc.

### Anthropic Files API

- Max file size: 20 MB per file
- File retention: 1 day (or duration of conversation)
- Supported formats: JSON, PDF, TXT, etc.

### Best Practices

1. **Export on demand** - Don't export every vCon
2. **Clean up files** - Delete old files regularly
3. **Organize by purpose** - Use clear naming conventions
4. **Monitor usage** - Track API costs and file count
5. **Test first** - Use small batches before full export

## Next Steps

- [API Reference](api-reference.md) - Complete API docs
- [Examples](examples.md) - More code examples
- [Configuration](../01-getting-started/configuration.md) - Configuration guide
- [Debugging](../03-testing/scenarios.md) - Troubleshooting

---

For more information:
- [OpenAI Files API](https://platform.openai.com/docs/api-reference/files)
- [Anthropic Files API](https://docs.anthropic.com)
