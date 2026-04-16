"""
Examples: AI Integrations with OpenAI and Anthropic

Demonstrates how to export vCons to OpenAI and Anthropic for AI analysis.
"""

import os
from src.adapter import ElevenLabsVconAdapter
from src.exporters.openai_exporter import OpenAIExporter
from src.exporters.anthropic_exporter import AnthropicExporter


def example_1_basic_openai_export():
    """Example 1: Export a vCon to OpenAI"""
    print("\n=== Example 1: Basic OpenAI Export ===\n")

    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()

    if not vcons:
        print("No vCons to export")
        return

    # Export first vCon to OpenAI
    exporter = OpenAIExporter(api_key=os.getenv('OPENAI_API_KEY'))
    result = exporter.export(vcons[0])

    print(f"Uploaded to OpenAI")
    print(f"  File ID: {result['file_id']}")
    print(f"  Size: {result['size']} bytes")
    print(f"  Status: {result['status']}")


def example_2_batch_export_openai():
    """Example 2: Batch export multiple vCons to OpenAI"""
    print("\n=== Example 2: Batch Export to OpenAI ===\n")

    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()

    exporter = OpenAIExporter(api_key=os.getenv('OPENAI_API_KEY'))
    results = exporter.export_batch(vcons)

    print(f"Batch uploaded {len(results)} vCons to OpenAI")
    for i, result in enumerate(results, 1):
        if 'error' not in result:
            print(f"  {i}. {result['file_id']}")
        else:
            print(f"  {i}. Error: {result['error']}")


def example_3_openai_with_assistants():
    """Example 3: Use uploaded vCons with OpenAI Assistants"""
    print("\n=== Example 3: Use with OpenAI Assistants ===\n")

    try:
        from openai import OpenAI
    except ImportError:
        print("Install openai: pip install openai")
        return

    # Upload vCon
    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()

    if not vcons:
        print("No vCons to process")
        return

    openai_exporter = OpenAIExporter(api_key=os.getenv('OPENAI_API_KEY'))
    result = openai_exporter.export(vcons[0])
    file_id = result['file_id']

    # Create assistant
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    assistant = client.beta.assistants.create(
        name="Conversation Analyzer",
        instructions="Analyze the provided conversation and extract key insights.",
        model="gpt-4-turbo-preview",
        tools=[{"type": "retrieval"}],
        file_ids=[file_id]
    )

    print(f"Created assistant: {assistant.id}")
    print(f"Using file: {file_id}")

    # Create thread and message
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please analyze this conversation and provide key insights."
    )

    print(f"\nThread: {thread.id}")
    print(f"Message: {message.id}")
    print("Run assistant to analyze conversation...")


def example_4_anthropic_export():
    """Example 4: Export vCons to Anthropic"""
    print("\n=== Example 4: Anthropic Export ===\n")

    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()

    if not vcons:
        print("No vCons to export")
        return

    exporter = AnthropicExporter(api_key=os.getenv('ANTHROPIC_API_KEY'))
    result = exporter.export(vcons[0])

    print(f"Uploaded to Anthropic")
    print(f"  File ID: {result['file_id']}")
    print(f"  Size: {result['size']} bytes")
    print(f"  Status: {result['status']}")


def example_5_anthropic_with_claude():
    """Example 5: Use uploaded vCons with Claude (RAG)"""
    print("\n=== Example 5: Use with Claude (RAG) ===\n")

    try:
        from anthropic import Anthropic
    except ImportError:
        print("Install anthropic: pip install anthropic")
        return

    # Upload vCon
    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()

    if not vcons:
        print("No vCons to process")
        return

    anthropic_exporter = AnthropicExporter(api_key=os.getenv('ANTHROPIC_API_KEY'))
    result = anthropic_exporter.export(vcons[0])
    file_id = result['file_id']

    # Query with Claude
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system="You are a conversation analyst. Analyze the provided conversation.",
        messages=[
            {
                "role": "user",
                "content": f"Please analyze this conversation (file: {file_id}). "
                          "Extract key insights, topics discussed, and sentiment."
            }
        ]
    )

    print(f"Claude Response:")
    print(message.content[0].text)


def example_6_list_and_manage_files():
    """Example 6: List and manage uploaded files"""
    print("\n=== Example 6: List and Manage Files ===\n")

    # OpenAI
    openai_exporter = OpenAIExporter(api_key=os.getenv('OPENAI_API_KEY'))
    print("OpenAI Files:")
    openai_files = list(openai_exporter.list_files(purpose="assistants"))
    print(f"  Total: {len(openai_files)}")
    for file in openai_files[:3]:
        print(f"    - {file.filename} ({file.id})")

    # Anthropic
    anthropic_exporter = AnthropicExporter(api_key=os.getenv('ANTHROPIC_API_KEY'))
    print("\nAnthropic Files:")
    anthropic_files = anthropic_exporter.list_files()
    print(f"  Total: {len(anthropic_files)}")
    for file in anthropic_files[:3]:
        print(f"    - {file.filename} ({file.id})")


def example_7_configuration_driven():
    """Example 7: Configuration-driven export to all platforms"""
    print("\n=== Example 7: Configuration-Driven Export ===\n")

    # config.yml should have:
    # exporters:
    #   openai:
    #     enabled: true
    #   anthropic:
    #     enabled: true

    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()

    print(f"Processed {len(vcons)} conversations")
    print("Exported to:")
    print("  - Local files")
    if 'openai' in adapter.exporters and adapter.exporters['openai']:
        print("  - OpenAI")
    if 'anthropic' in adapter.exporters and adapter.exporters['anthropic']:
        print("  - Anthropic")


def example_8_error_handling():
    """Example 8: Error handling for AI exports"""
    print("\n=== Example 8: Error Handling ===\n")

    try:
        # Try to export without API key
        exporter = OpenAIExporter(api_key=None)
    except ValueError as e:
        print(f"Caught ValueError: {e}")

    try:
        # Try with missing package
        from anthropic import Anthropic
        print("Anthropic SDK is installed")
    except ImportError:
        print("Anthropic SDK not installed - install with: pip install anthropic")

    # Safe batch export
    adapter = ElevenLabsVconAdapter(config_file='config.yml')
    vcons = adapter.process_all()

    exporter = OpenAIExporter(api_key=os.getenv('OPENAI_API_KEY'))
    results = exporter.export_batch(vcons)

    successful = [r for r in results if 'error' not in r]
    failed = [r for r in results if 'error' in r]

    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")


if __name__ == "__main__":
    print("=" * 60)
    print("AI Integration Examples")
    print("=" * 60)

    # Set up environment
    if not os.getenv('OPENAI_API_KEY'):
        print("\nWARNING: OPENAI_API_KEY not set")
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("WARNING: ANTHROPIC_API_KEY not set\n")

    # Run examples (comment out as needed)
    try:
        # example_1_basic_openai_export()
        # example_2_batch_export_openai()
        # example_3_openai_with_assistants()
        # example_4_anthropic_export()
        # example_5_anthropic_with_claude()
        # example_6_list_and_manage_files()
        example_7_configuration_driven()
        # example_8_error_handling()
    except Exception as e:
        print(f"\nError: {e}")
        print("Check that API keys are set and packages are installed")
