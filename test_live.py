#!/usr/bin/env python3
"""
Interactive Live Testing Script for ElevenLabs vCon Adapter

This script guides you through setting up and testing the adapter
with your real ElevenLabs account.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_section(text):
    """Print a formatted section"""
    print(f"\n--- {text} ---\n")

def test_api_connection(api_key):
    """Test connection to ElevenLabs API"""
    print_section("Testing ElevenLabs API Connection")
    
    try:
        from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
        
        print("Initializing ElevenLabs extractor...")
        extractor = ElevenLabsExtractor(api_key=api_key)
        
        print("Fetching agents from ElevenLabs...")
        agents = extractor.list_agents()
        
        print(f"SUCCESS! Found {len(agents)} agent(s):\n")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. Name: {agent.name}")
            print(f"     ID: {agent.id}")
            if hasattr(agent, 'phone_number') and agent.phone_number:
                print(f"     Phone: {agent.phone_number}")
            print()
        
        return agents
        
    except Exception as e:
        print(f"ERROR: Failed to connect to ElevenLabs API")
        print(f"Details: {str(e)}\n")
        print("Please check:")
        print("  1. Your API key is correct")
        print("  2. You have internet connectivity")
        print("  3. ElevenLabs service is accessible")
        return None

def select_agent(agents):
    """Prompt user to select an agent"""
    if not agents:
        return None
    
    if len(agents) == 1:
        print(f"Using agent: {agents[0].name} ({agents[0].id})")
        return agents[0].id
    
    print_section("Select an Agent")
    for i, agent in enumerate(agents, 1):
        print(f"  {i}. {agent.name} (ID: {agent.id})")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the agent to process: "))
            if 1 <= choice <= len(agents):
                return agents[choice - 1].id
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def check_conversations(api_key, agent_id):
    """Check if agent has any conversations"""
    print_section("Checking for Conversations")
    
    try:
        from src.extractors.elevenlabs_extractor import ElevenLabsExtractor
        
        extractor = ElevenLabsExtractor(api_key=api_key)
        conversations = extractor.get_agent_conversations(agent_id)
        
        if conversations:
            print(f"Found {len(conversations)} conversation(s):\n")
            for i, conv in enumerate(conversations[:5], 1):  # Show first 5
                print(f"  {i}. ID: {conv.id}")
                print(f"     Start: {conv.start_time}")
                if hasattr(conv, 'duration'):
                    print(f"     Duration: {conv.duration}s")
                print()
            if len(conversations) > 5:
                print(f"  ... and {len(conversations) - 5} more\n")
            return True
        else:
            print("No conversations found for this agent.\n")
            print("Next steps:")
            print("  1. Call the phone number attached to this agent")
            print("  2. Have a conversation with the AI agent")
            print("  3. Wait 1-2 minutes for the call to be processed")
            print("  4. Run this script again to check for new conversations")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not fetch conversations: {str(e)}")
        return False

def process_conversations(api_key, agent_id):
    """Process conversations for an agent"""
    print_section("Processing Conversations")
    
    try:
        from src.adapter import ElevenLabsVconAdapter
        
        print("Loading configuration...")
        config_file = 'config.yml'
        
        if not Path(config_file).exists():
            print(f"ERROR: {config_file} not found")
            print("Please run: cp config.yml.example config.yml")
            return []
        
        print("Initializing adapter...")
        adapter = ElevenLabsVconAdapter(config_file=config_file)
        
        print(f"Processing agent: {agent_id}...")
        vcons = adapter.process_agent(agent_id)
        
        print(f"\nSUCCESS! Created {len(vcons)} vCon(s)\n")
        
        if vcons:
            print("Created vCons:")
            for i, vcon in enumerate(vcons, 1):
                print(f"  {i}. UUID: {vcon.uuid}")
                print(f"     Subject: {vcon.subject or 'N/A'}")
                print(f"     Parties: {len(vcon.parties)}")
                print(f"     Dialog: {len(vcon.dialog) if vcon.dialog else 0}")
                print()
        
        return vcons
        
    except Exception as e:
        print(f"ERROR: Failed to process conversations: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def verify_output():
    """Verify vCon files were created"""
    print_section("Verifying Output")
    
    vcon_dir = Path('./vcons')
    
    if not vcon_dir.exists():
        print("vcons directory not found")
        return False
    
    vcon_files = list(vcon_dir.glob('vcon_*.json'))
    
    if not vcon_files:
        print("No vCon files found in ./vcons/")
        return False
    
    print(f"Found {len(vcon_files)} vCon file(s):\n")
    
    # Show latest vCon
    latest_vcon = sorted(vcon_files, key=lambda x: x.stat().st_mtime)[-1]
    
    try:
        with open(latest_vcon) as f:
            vcon_data = json.load(f)
        
        print(f"Latest vCon: {latest_vcon.name}")
        print(f"  UUID: {vcon_data.get('uuid')}")
        print(f"  Subject: {vcon_data.get('subject', 'N/A')}")
        print(f"  Created: {vcon_data.get('created', 'N/A')}")
        print(f"  Parties: {len(vcon_data.get('parties', []))}")
        print(f"  Dialog Entries: {len(vcon_data.get('dialog', []))}")
        print(f"  Attachments: {len(vcon_data.get('attachments', []))}")
        print(f"  Analysis: {len(vcon_data.get('analysis', []))}")
        print(f"\nFile size: {latest_vcon.stat().st_size / 1024:.2f} KB")
        print(f"Location: {latest_vcon.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"ERROR reading vCon file: {str(e)}")
        return False

def get_api_key():
    """Get API key from environment or user input"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if api_key:
        print(f"Using API key from environment: {api_key[:10]}...")
        return api_key
    
    print_section("Enter Your API Key")
    print("Enter your ElevenLabs API key:")
    print("(You can get this from https://elevenlabs.io/app/settings/api-keys)\n")
    
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("ERROR: API key is required")
        return None
    
    # Optionally save to environment
    save = input("\nSave API key to environment? (y/n): ").strip().lower()
    if save == 'y':
        print("\nAdd this to your shell profile or run:")
        print(f'export ELEVENLABS_API_KEY="{api_key}"')
    
    return api_key

def show_menu():
    """Show main menu"""
    print_header("ElevenLabs vCon Adapter - Live Testing")
    
    print("This tool will help you configure and test the adapter with your")
    print("real ElevenLabs account.\n")
    
    print("Available options:")
    print("  1. Test API connection and list agents")
    print("  2. Check conversations for an agent")
    print("  3. Process conversations and create vCons")
    print("  4. Verify output files")
    print("  5. Full test (steps 1-4)")
    print("  6. Exit\n")
    
    return input("Select an option (1-6): ").strip()

def main():
    """Main function"""
    try:
        # Create vcons directory if needed
        Path('./vcons').mkdir(exist_ok=True)
        
        while True:
            choice = show_menu()
            
            if choice == '1':
                api_key = get_api_key()
                if api_key:
                    test_api_connection(api_key)
            
            elif choice == '2':
                api_key = get_api_key()
                if api_key:
                    agents = test_api_connection(api_key)
                    if agents:
                        agent_id = select_agent(agents)
                        if agent_id:
                            check_conversations(api_key, agent_id)
            
            elif choice == '3':
                api_key = get_api_key()
                if api_key:
                    agents = test_api_connection(api_key)
                    if agents:
                        agent_id = select_agent(agents)
                        if agent_id:
                            process_conversations(api_key, agent_id)
            
            elif choice == '4':
                verify_output()
            
            elif choice == '5':
                print_header("Running Full Test")
                api_key = get_api_key()
                if api_key:
                    agents = test_api_connection(api_key)
                    if agents:
                        agent_id = select_agent(agents)
                        if agent_id:
                            has_conversations = check_conversations(api_key, agent_id)
                            if has_conversations:
                                vcons = process_conversations(api_key, agent_id)
                                if vcons:
                                    verify_output()
                            else:
                                print("Skipping processing - no conversations found")
            
            elif choice == '6':
                print("\nGoodbye!")
                sys.exit(0)
            
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
