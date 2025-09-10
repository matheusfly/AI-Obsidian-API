#!/usr/bin/env python3
"""
Test Live Vault Synchronization System
Comprehensive testing of file watching, incremental updates, and startup sync
"""

import asyncio
import logging
import tempfile
import shutil
from pathlib import Path
from src.monitoring.vault_monitor import VaultMonitorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_live_vault_sync():
    """Test the complete live vault synchronization system"""
    
    print("🚀 TESTING LIVE VAULT SYNCHRONIZATION SYSTEM")
    print("=" * 60)
    
    # Create a temporary test vault
    with tempfile.TemporaryDirectory() as temp_dir:
        test_vault_path = Path(temp_dir) / "test_vault"
        test_vault_path.mkdir()
        
        print(f"📁 Created test vault: {test_vault_path}")
        
        # Create some test files
        test_files = {
            "test1.md": "# Test File 1\n\nThis is a test file for vault synchronization.\n\n## Section 1\n\nContent here.\n\n#tag1 #tag2",
            "test2.md": "# Test File 2\n\nAnother test file with different content.\n\n## Section A\n\nMore content here.\n\n#tag3 #tag4",
            "nested/test3.md": "# Nested Test File\n\nThis file is in a nested directory.\n\n## Nested Section\n\nNested content.\n\n#nested #test"
        }
        
        # Create nested directory
        (test_vault_path / "nested").mkdir()
        
        # Write test files
        for file_path, content in test_files.items():
            full_path = test_vault_path / file_path
            full_path.write_text(content, encoding='utf-8')
            print(f"📄 Created test file: {file_path}")
        
        # Test 1: Initialize Vault Monitor
        print("\n🔧 TEST 1: Initialize Vault Monitor")
        print("-" * 40)
        
        vault_monitor = VaultMonitorService(
            vault_path=str(test_vault_path),
            chroma_db_path="./test_chroma_db",
            collection_name="test_live_sync",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            debounce_delay=1.0  # Shorter delay for testing
        )
        
        print("✅ Vault monitor initialized successfully")
        
        # Test 2: Startup Synchronization
        print("\n🚀 TEST 2: Startup Synchronization")
        print("-" * 40)
        
        startup_result = await vault_monitor.start()
        
        if startup_result.get('success', False):
            print("✅ Startup synchronization successful")
            print(f"📊 Startup time: {startup_result.get('startup_time_ms', 0):.2f}ms")
            
            sync_result = startup_result.get('sync_result', {})
            print(f"📊 Filesystem files: {sync_result.get('filesystem_files', 0)}")
            print(f"📊 ChromaDB files: {sync_result.get('chromadb_files', 0)}")
            
            sync_plan = sync_result.get('sync_plan', {})
            print(f"📊 New files: {len(sync_plan.get('new_files', []))}")
            print(f"📊 Modified files: {len(sync_plan.get('modified_files', []))}")
            print(f"📊 Deleted files: {len(sync_plan.get('deleted_files', []))}")
        else:
            print(f"❌ Startup synchronization failed: {startup_result.get('error')}")
            return False
        
        # Test 3: File Modification Test
        print("\n📝 TEST 3: File Modification Test")
        print("-" * 40)
        
        # Modify a file
        test_file_path = test_vault_path / "test1.md"
        original_content = test_file_path.read_text()
        modified_content = original_content + "\n\n## New Section\n\nThis is new content added for testing.\n\n#newtag"
        test_file_path.write_text(modified_content)
        
        print("📝 Modified test1.md")
        
        # Wait for debounced processing
        await asyncio.sleep(2.0)
        
        # Check status
        status = await vault_monitor.get_status()
        monitor_stats = status.get('monitor_stats', {})
        
        print(f"📊 Files processed: {monitor_stats.get('files_processed', 0)}")
        print(f"📊 Total chunks processed: {monitor_stats.get('total_chunks_processed', 0)}")
        print(f"📊 Processing time: {monitor_stats.get('total_processing_time_ms', 0):.2f}ms")
        print(f"📊 Errors: {monitor_stats.get('errors', 0)}")
        
        # Test 4: File Creation Test
        print("\n📄 TEST 4: File Creation Test")
        print("-" * 40)
        
        # Create a new file
        new_file_path = test_vault_path / "new_test.md"
        new_content = "# New Test File\n\nThis is a newly created file for testing.\n\n## New Content\n\nTesting file creation.\n\n#newfile #test"
        new_file_path.write_text(new_content)
        
        print("📄 Created new_test.md")
        
        # Wait for debounced processing
        await asyncio.sleep(2.0)
        
        # Check updated status
        status = await vault_monitor.get_status()
        monitor_stats = status.get('monitor_stats', {})
        
        print(f"📊 Files processed: {monitor_stats.get('files_processed', 0)}")
        print(f"📊 Total chunks processed: {monitor_stats.get('total_chunks_processed', 0)}")
        
        # Test 5: File Deletion Test
        print("\n🗑️ TEST 5: File Deletion Test")
        print("-" * 40)
        
        # Delete a file
        delete_file_path = test_vault_path / "test2.md"
        delete_file_path.unlink()
        
        print("🗑️ Deleted test2.md")
        
        # Wait for debounced processing
        await asyncio.sleep(2.0)
        
        # Check updated status
        status = await vault_monitor.get_status()
        monitor_stats = status.get('monitor_stats', {})
        
        print(f"📊 Files deleted: {monitor_stats.get('files_deleted', 0)}")
        print(f"📊 Total errors: {monitor_stats.get('errors', 0)}")
        
        # Test 6: Force Sync Test
        print("\n🔄 TEST 6: Force Sync Test")
        print("-" * 40)
        
        # Force sync the remaining file
        force_sync_result = await vault_monitor.force_sync_file("test1.md")
        
        if force_sync_result.get('success', False):
            print("✅ Force sync successful")
            print(f"📊 Chunks processed: {force_sync_result.get('chunks_processed', 0)}")
            print(f"📊 Processing time: {force_sync_result.get('processing_time_ms', 0):.2f}ms")
        else:
            print(f"❌ Force sync failed: {force_sync_result.get('error')}")
        
        # Test 7: Batch Sync Test
        print("\n📦 TEST 7: Batch Sync Test")
        print("-" * 40)
        
        # Create multiple files for batch processing
        batch_files = ["test1.md", "new_test.md", "nested/test3.md"]
        
        batch_result = await vault_monitor.batch_sync_files(batch_files)
        
        if batch_result.get('success', False):
            print("✅ Batch sync successful")
            print(f"📊 Files processed: {batch_result.get('successful', 0)}")
            print(f"📊 Files failed: {batch_result.get('failed', 0)}")
            print(f"📊 Total chunks: {batch_result.get('total_chunks', 0)}")
            print(f"📊 Processing time: {batch_result.get('processing_time_ms', 0):.2f}ms")
        else:
            print(f"❌ Batch sync failed: {batch_result.get('error')}")
        
        # Test 8: Final Status Check
        print("\n📊 TEST 8: Final Status Check")
        print("-" * 40)
        
        final_status = await vault_monitor.get_status()
        
        print("📊 Final System Status:")
        print(f"  Running: {final_status.get('is_running', False)}")
        print(f"  Startup Complete: {final_status.get('startup_complete', False)}")
        
        file_watcher = final_status.get('file_watcher', {})
        print(f"  File Watcher Running: {file_watcher.get('is_running', False)}")
        print(f"  Pending Tasks: {file_watcher.get('pending_tasks', 0)}")
        
        processing_stats = final_status.get('processing_stats', {})
        print(f"  Total Chunks in DB: {processing_stats.get('total_chunks', 0)}")
        
        monitor_stats = final_status.get('monitor_stats', {})
        print(f"  Files Processed: {monitor_stats.get('files_processed', 0)}")
        print(f"  Files Deleted: {monitor_stats.get('files_deleted', 0)}")
        print(f"  Total Errors: {monitor_stats.get('errors', 0)}")
        
        # Test 9: Graceful Shutdown
        print("\n🛑 TEST 9: Graceful Shutdown")
        print("-" * 40)
        
        await vault_monitor.stop()
        print("✅ Graceful shutdown completed")
        
        # Cleanup test ChromaDB
        try:
            shutil.rmtree("./test_chroma_db")
            print("🧹 Cleaned up test ChromaDB")
        except Exception as e:
            print(f"⚠️ Could not clean up test ChromaDB: {e}")
        
        print("\n🎉 LIVE VAULT SYNCHRONIZATION TEST COMPLETE!")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    success = asyncio.run(test_live_vault_sync())
    exit(0 if success else 1)
