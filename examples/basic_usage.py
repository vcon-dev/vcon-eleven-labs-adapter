#!/usr/bin/env python3
"""
Basic usage example for the ElevenLabs vCon Adapter

This example demonstrates how to:
1. Initialize the adapter
2. Process conversations from ElevenLabs
3. Export vCons to file, S3, and webhooks
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapter import ElevenLabsVconAdapter


def main():
    """Main example function"""

    print("Starting ElevenLabs vCon Adapter Example")
    print("-" * 50)

    try:
        adapter = ElevenLabsVconAdapter(config_file="config.yml")

        print("\nAdapter initialized successfully!")
        print(f"Metrics: {adapter.get_metrics()}")

        print("\nProcessing all agents...")
        vcons = adapter.process_all()

        print(f"\nSuccessfully created {len(vcons)} vCons")

        for vcon in vcons:
            print(f"  - {vcon.uuid}")

        print("\nAll vCons have been exported!")

    except FileNotFoundError as e:
        print(f"Error: Configuration file not found - {e}")
        print("Please create config.yml from config.yml.example")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def example_process_single_agent():
    """Example: Process a single agent"""
    adapter = ElevenLabsVconAdapter(config_file="config.yml")

    agent_id = "your_agent_id_here"
    vcons = adapter.process_agent(agent_id)

    print(f"Processed {len(vcons)} conversations for agent {agent_id}")


def example_custom_export():
    """Example: Export to specific backends"""
    adapter = ElevenLabsVconAdapter(config_file="config.yml")

    vcons = adapter.process_all()

    if vcons:
        vcon = vcons[0]

        if "file" in adapter.exporters:
            print("Exporting to file...")
            adapter.exporters["file"].export(vcon)

        if "s3" in adapter.exporters:
            print("Exporting to S3...")
            adapter.exporters["s3"].export(vcon)

        if "webhook" in adapter.exporters:
            print("Exporting to webhook...")
            adapter.exporters["webhook"].export(vcon)


if __name__ == "__main__":
    main()
