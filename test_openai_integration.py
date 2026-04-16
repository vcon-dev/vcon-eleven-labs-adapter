"""
Test OpenAI Integration

This script processes ElevenLabs conversations into vCons and exports them to OpenAI.
Also adds them to a vector store for retrieval.
"""

import os
import sys
from src.adapter import ElevenLabsVconAdapter
from src.exporters.openai_exporter import OpenAIExporter


def test_openai_export_and_vector_store():
    """Test exporting vCons to OpenAI and adding to vector store"""
    
    print("\n" + "="*80)
    print("OPENAI INTEGRATION TEST WITH VECTOR STORE")
    print("="*80 + "\n")
    
    # Configuration — set OPENAI_API_KEY in your environment
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    vector_store_id = "vs_68f2b4d1c398819198188159b44fad09"
    
    try:
        # Step 1: Initialize OpenAI exporter
        print("Step 1: Initializing OpenAI exporter...")
        openai_exporter = OpenAIExporter(api_key=openai_api_key, purpose="assistants")
        print("✓ OpenAI exporter initialized successfully")
        
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
        
        # Step 3: Export to OpenAI
        print("\nStep 3: Exporting vCons to OpenAI Files API...")
        results = openai_exporter.export_batch(vcons)
        
        # Step 4: Display results
        print("\nStep 4: Upload Results\n")
        successful = 0
        failed = 0
        file_ids = []
        
        for i, (vcon, result) in enumerate(zip(vcons, results), 1):
            if 'error' not in result:
                successful += 1
                file_ids.append(result['file_id'])
                print(f"✓ vCon {i}: Successfully uploaded")
                print(f"  File ID: {result['file_id']}")
                print(f"  Size: {result['size']} bytes")
                print(f"  Status: {result['status']}")
                print()
            else:
                failed += 1
                print(f"✗ vCon {i}: Failed to upload")
                print(f"  Error: {result['error']}\n")
        
        # Step 5: Try to add files to vector store
        print("\nStep 5: Adding all files to vector store...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            # Add ALL files to vector store
            added_count = 0
            for i, file_id in enumerate(file_ids, 1):
                try:
                    response = client.vector_stores.files.create(
                        vector_store_id=vector_store_id,
                        file_id=file_id
                    )
                    added_count += 1
                    if i % 10 == 0:
                        print(f"  ✓ Added {i} files to vector store...")
                except Exception as e:
                    print(f"  ✗ Failed to add {file_id}: {e}")
            
            print(f"\n✓ Successfully added {added_count}/{len(file_ids)} files to vector store!")
            
        except ImportError:
            print("  Note: OpenAI SDK features not fully available")
        except Exception as e:
            print(f"  Note: Vector store operations: {e}")
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total vCons processed: {len(vcons)}")
        print(f"Successfully uploaded:  {successful}")
        print(f"Failed uploads:         {failed}")
        
        if successful > 0:
            print(f"\n✓ SUCCESS: {successful} vCons exported to OpenAI!")
            print(f"  File IDs: {file_ids[:3]}...")
            print(f"  Vector Store ID: {vector_store_id}")
            
            # List all files in OpenAI
            print("\nStep 6: Listing files in OpenAI...")
            try:
                all_files = list(openai_exporter.list_files(purpose="assistants"))
                print(f"Total files in OpenAI: {len(all_files)}")
                
                if len(all_files) > 0:
                    print("\nRecent files:")
                    for file_obj in all_files[:5]:
                        print(f"  • {file_obj.filename} (ID: {file_obj.id})")
                        print(f"    Size: {file_obj.size_bytes} bytes")
            except Exception as e:
                print(f"  Note: Could not list files: {e}")
        else:
            print("\n✗ FAILED: No vCons were successfully exported")
        
        print("\n" + "="*80 + "\n")
        
    except ImportError as e:
        print(f"\n✗ ERROR: Missing dependency")
        print(f"  {e}")
        print("\nInstall with: pip install openai")
    except ValueError as e:
        print(f"\n✗ ERROR: Configuration error")
        print(f"  {e}")
    except Exception as e:
        print(f"\n✗ ERROR: Test failed")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_openai_export_and_vector_store()
