"""
Test Anthropic Integration

This script processes ElevenLabs conversations into vCons and exports them to Anthropic.
"""

import os
import sys
from src.adapter import ElevenLabsVconAdapter
from src.exporters.anthropic_exporter import AnthropicExporter


def test_anthropic_export():
    """Test exporting vCons to Anthropic"""
    
    print("\n" + "="*80)
    print("ANTHROPIC INTEGRATION TEST")
    print("="*80 + "\n")
    
    # Configuration — set ANTHROPIC_API_KEY in your environment
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    
    try:
        # Step 1: Initialize Anthropic exporter
        print("Step 1: Initializing Anthropic exporter...")
        anthropic_exporter = AnthropicExporter(api_key=anthropic_api_key)
        print("✓ Anthropic exporter initialized successfully")
        
        # Step 2: Initialize adapter and process vCons
        print("\nStep 2: Loading vCon adapter and processing conversations...")
        adapter = ElevenLabsVconAdapter(config_file='config.yml')
        print("✓ Adapter initialized")
        
        # Process all conversations
        print("  Processing conversations...")
        vcons = adapter.process_all()
        print(f"✓ Processed {len(vcons)} conversations into vCons")
        
        if not vcons:
            print("\n⚠ No conversations found to export")
            print("  Tip: Make sure your ElevenLabs agent has recent conversations")
            return
        
        # Step 3: Export to Anthropic
        print("\nStep 3: Exporting vCons to Anthropic...")
        results = anthropic_exporter.export_batch(vcons)
        
        # Step 4: Display results
        print("\nStep 4: Results\n")
        successful = 0
        failed = 0
        
        for i, (vcon, result) in enumerate(zip(vcons, results), 1):
            if 'error' not in result:
                successful += 1
                print(f"✓ vCon {i}: Successfully uploaded")
                print(f"  File ID: {result['file_id']}")
                print(f"  Size: {result['size']} bytes")
                print(f"  Status: {result['status']}")
                
                # List file details
                try:
                    file_info = anthropic_exporter.retrieve_file(result['file_id'])
                    print(f"  Filename: {file_info['filename']}")
                    print(f"  Created: {file_info['created_at']}")
                except Exception as e:
                    print(f"  (Could not retrieve details: {e})")
                print()
            else:
                failed += 1
                print(f"✗ vCon {i}: Failed to upload")
                print(f"  Error: {result['error']}\n")
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total vCons processed: {len(vcons)}")
        print(f"Successfully uploaded:  {successful}")
        print(f"Failed uploads:         {failed}")
        
        if successful > 0:
            print(f"\n✓ SUCCESS: {successful} vCons exported to Anthropic!")
            
            # List all files in Anthropic
            print("\nStep 5: Listing all files in Anthropic...")
            all_files = anthropic_exporter.list_files()
            print(f"Total files in Anthropic: {len(all_files)}")
            
            if len(all_files) > 0:
                print("\nRecent files:")
                for file_obj in all_files[:5]:
                    print(f"  • {file_obj.filename} (ID: {file_obj.id})")
                    if hasattr(file_obj, 'size') and file_obj.size:
                        print(f"    Size: {file_obj.size} bytes")
        else:
            print("\n✗ FAILED: No vCons were successfully exported")
        
        print("\n" + "="*80 + "\n")
        
    except ImportError as e:
        print(f"\n✗ ERROR: Missing dependency")
        print(f"  {e}")
        print("\nInstall with: pip install anthropic")
    except ValueError as e:
        print(f"\n✗ ERROR: Configuration error")
        print(f"  {e}")
    except Exception as e:
        print(f"\n✗ ERROR: Test failed")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_anthropic_export()
