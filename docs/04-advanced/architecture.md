# Architecture Overview

Complete system design and component relationships for the vCon ElevenLabs Adapter.

## System Architecture

```
ElevenLabs API (cloud)
    |
    v
┌─────────────────────────────────────────┐
│     ElevenLabsVconAdapter (Main)        │
│  - Orchestrates all components          │
│  - Manages configuration                │
│  - Tracks metrics                       │
└─────────────────────────────────────────┘
    |
    +---> ElevenLabsExtractor
    |     - Fetch agents
    |     - Get conversations
    |     - Download audio
    |
    +---> PartyMapper + DialogProcessor + VconBuilder
    |     - Transform to vCon format
    |     - Build complete vCon objects
    |
    +---> FileExporter
    |     - Save to local filesystem
    |
    +---> S3Exporter
    |     - Upload to AWS S3
    |
    +---> WebhookExporter
    |     - POST to webhooks
```

## Component Details

### ElevenLabsVconAdapter

**Purpose**: Main orchestrator class

**Responsibilities**:
- Load and validate configuration
- Initialize extractors and exporters
- Coordinate processing workflow
- Track metrics and errors
- Manage logging

**Key Methods**:
- `process_all()` - Process all agents
- `process_agent(agent_id)` - Process specific agent
- `get_metrics()` - Get processing statistics

### ElevenLabsExtractor

**Purpose**: Interact with ElevenLabs API

**Responsibilities**:
- Connect to ElevenLabs API
- Fetch agent list
- Retrieve conversations
- Download audio files
- Handle API errors with retry logic

**Features**:
- Exponential backoff retry
- Comprehensive error handling
- Timeout management
- Rate limit awareness

### Transformers

#### PartyMapper
**Purpose**: Convert participants to vCon parties

**Process**:
- Read conversation participants
- Map to vCon Party format
- Identify roles (agent, customer)
- Handle missing data gracefully

#### DialogProcessor
**Purpose**: Convert conversations to vCon dialogs

**Process**:
- Extract audio from conversations
- Extract transcripts
- Create vCon dialog objects
- Handle multiple formats

#### VconBuilder
**Purpose**: Assemble complete vCon objects

**Process**:
- Combine parties and dialogs
- Add metadata
- Add attachments
- Add analysis
- Validate vCon

### Exporters

#### FileExporter
**Purpose**: Save vCons to filesystem

**Features**:
- Configurable output directory
- Filename templating
- Overwrite protection
- Error handling

#### S3Exporter
**Purpose**: Upload vCons to AWS S3

**Features**:
- Server-side encryption (AES256/KMS)
- Custom metadata/tags
- Retry logic
- Batch operations

#### WebhookExporter
**Purpose**: POST vCons to HTTP endpoints

**Features**:
- Multiple auth types (Bearer, API Key)
- Retry with exponential backoff
- Batch requests
- Timeout handling

## Data Flow

### Processing Pipeline

```
1. Load Configuration
   |
   v
2. Initialize Components
   |
   v
3. Extract Phase
   |
   +---> Fetch agents
   |
   +---> For each agent:
         - Get conversations
         - Download audio
   |
   v
4. Transform Phase
   |
   +---> For each conversation:
         - Map parties
         - Process dialogs
         - Build vCon
   |
   v
5. Export Phase
   |
   +---> For each vCon:
         - File export
         - S3 export
         - Webhook export
   |
   v
6. Report Metrics
```

### Error Handling

```
API Call
    |
    +---> Success: Return data
    |
    +---> Error:
          |
          +---> Retry logic
          |     - Exponential backoff
          |     - Max retries check
          |
          +---> Log error
          |
          +---> Graceful degradation
          |     - Continue processing
          |     - Track error count
```

## Configuration Structure

```
Config
├── ElevenLabs Settings
│   ├── API Key
│   ├── Agent IDs
│   ├── Timeout
│   ├── Batch size
│   └── Poll interval
│
├── Exporters
│   ├── File
│   │   ├── Directory
│   │   └── Overwrite policy
│   ├── S3
│   │   ├── Bucket
│   │   ├── Region
│   │   ├── Prefix
│   │   └── Encryption
│   └── Webhook
│       ├── URL
│       ├── Auth
│       └── Retry settings
│
├── Logging
│   ├── Level
│   ├── File path
│   ├── Format
│   └── Console output
│
└── vCon Options
    ├── Include analysis
    └── Include attachments
```

## Modular Design

### Independent Components

Each component can be used independently:

```python
# Use just the extractor
extractor = ElevenLabsExtractor(api_key=key)
agents = extractor.list_agents()

# Use just the transformer
builder = VconBuilder()
vcon = builder.build_vcon(conversation)

# Use just an exporter
exporter = FileExporter(directory='./output')
exporter.export(vcon)
```

### Loose Coupling

Components communicate through:
- Configuration objects
- Data models
- Standard return types

Changes to one component don't affect others.

## Type Safety

### Pydantic Models

All data is validated using Pydantic models:

```python
class Agent(BaseModel):
    id: str
    name: str
    status: str
    created_at: Optional[datetime] = None

class Conversation(BaseModel):
    id: str
    agent_id: str
    start_time: datetime
    participants: List[ConversationParticipant]
    # ... more fields
```

Benefits:
- Type checking
- Data validation
- Auto-documentation
- Serialization support

## Extensibility

### Adding New Exporters

```python
from src.exporters.file_exporter import FileExporter

class DatabaseExporter(FileExporter):
    def export(self, vcon):
        # Save to database
        db.insert(vcon)
```

### Adding New Data Sources

```python
from src.extractors.elevenlabs_extractor import ElevenLabsExtractor

class ZoomExtractor(ElevenLabsExtractor):
    def list_agents(self):
        # Fetch from Zoom API
        return zoom_api.get_users()
```

## Performance Characteristics

### Processing Speed

- Average: 100-200ms per vCon
- Depends on:
  - Audio file size
  - Network latency
  - Disk I/O speed

### Memory Usage

- Per conversation: ~10-50MB
- Scales linearly with batch size
- Configurable batch size for memory constraints

### Network I/O

- One API call per agent
- One API call per batch of conversations
- Batch size configurable (default: 10)

## Scalability

### Horizontal Scaling

Process multiple agents in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)
for agent_id in agent_ids:
    executor.submit(adapter.process_agent, agent_id)
executor.shutdown()
```

### Vertical Scaling

Increase batch sizes:

```yaml
elevenlabs:
  batch_size: 50  # Process more conversations per call
```

## Deployment Options

### Local Execution

```bash
python3 examples/basic_usage.py
```

### Docker Container

```dockerfile
FROM python:3.8
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "examples/basic_usage.py"]
```

### Scheduled Processing (Cron)

```bash
0 */6 * * * /path/to/venv/bin/python /path/to/process.py
```

### Cloud Function (AWS Lambda)

```python
def lambda_handler(event, context):
    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()
    return {'statusCode': 200, 'body': f'Created {len(vcons)} vCons'}
```

## Logging Architecture

```
Logger
├── File Handler
│   ├── adapter.log (rolling file)
│   └── Configurable format
└── Console Handler
    ├── Standard output
    └── Configurable level
```

## Future Architecture Enhancements

### Planned Features

- **Async/await support** - Non-blocking I/O
- **Database backend** - Track processed conversations
- **Caching layer** - Reduce API calls
- **Message queue** - Decouple processing
- **Streaming** - Handle large files
- **Multi-tenant** - Serve multiple users

### Optimization Opportunities

- Connection pooling
- Response caching
- Batch API operations
- Parallel processing
- Memory optimization

---

For implementation details, see:
- [User Guide](../02-usage/user-guide.md)
- [API Reference](../02-usage/api-reference.md)
- [Configuration](../01-getting-started/configuration.md)
