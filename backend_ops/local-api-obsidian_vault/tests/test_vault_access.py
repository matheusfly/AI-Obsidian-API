#!/usr/bin/env python3
"""
Simple test script to access Obsidian vault and test basic functionality
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

# Configuration
VAULT_PATH = r"D:\Nomade Milionario"
VAULT_NAME = "Nomade Milionario"

def test_vault_access():
    """Test basic vault access"""
    print("🚀 OBSIDIAN VAULT AI SYSTEM - FIRST API TEST")
    print("=" * 60)
    
    # Test 1: Check if vault exists
    print(f"📁 Testing vault access: {VAULT_PATH}")
    if not os.path.exists(VAULT_PATH):
        print("❌ Vault path does not exist!")
        return False
    print("✅ Vault path exists")
    
    # Test 2: Count markdown files
    print("\n📄 Counting markdown files...")
    md_files = list(Path(VAULT_PATH).rglob("*.md"))
    print(f"✅ Found {len(md_files)} markdown files")
    
    # Test 3: List first 10 files
    print("\n📋 First 10 markdown files:")
    for i, file_path in enumerate(md_files[:10]):
        relative_path = file_path.relative_to(VAULT_PATH)
        print(f"  {i+1}. {relative_path}")
    
    # Test 4: Read a sample file
    if md_files:
        sample_file = md_files[0]
        print(f"\n📖 Reading sample file: {sample_file.name}")
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ File size: {len(content)} characters")
                print(f"✅ First 200 characters:")
                print(f"   {content[:200]}...")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    # Test 5: Search for files containing specific terms
    print("\n🔍 Searching for files containing 'AI' or 'agent'...")
    ai_files = []
    for file_path in md_files[:50]:  # Check first 50 files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if 'ai' in content or 'agent' in content:
                    ai_files.append(file_path.relative_to(VAULT_PATH))
        except:
            continue
    
    print(f"✅ Found {len(ai_files)} files containing 'AI' or 'agent'")
    for i, file_path in enumerate(ai_files[:5]):
        print(f"  {i+1}. {file_path}")
    
    # Test 6: Generate vault statistics
    print("\n📊 Vault Statistics:")
    
    # Count by directory
    dir_counts = {}
    for file_path in md_files:
        parent = file_path.parent.relative_to(VAULT_PATH)
        parent_str = str(parent) if parent != Path('.') else 'root'
        dir_counts[parent_str] = dir_counts.get(parent_str, 0) + 1
    
    # Show top directories
    sorted_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("📁 Top directories by file count:")
    for dir_name, count in sorted_dirs:
        print(f"  {dir_name}: {count} files")
    
    # Test 7: Create API response format
    print("\n🌐 Generating API response format...")
    api_response = {
        "status": "success",
        "vault": {
            "name": VAULT_NAME,
            "path": VAULT_PATH,
            "total_files": len(md_files),
            "directories": len(dir_counts),
            "sample_files": [str(f.relative_to(VAULT_PATH)) for f in md_files[:5]],
            "top_directories": dict(sorted_dirs[:5])
        },
        "search_results": {
            "ai_related_files": len(ai_files),
            "sample_matches": [str(f) for f in ai_files[:3]]
        }
    }
    
    print("✅ API Response:")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    print("\n🎉 VAULT ACCESS TEST COMPLETED SUCCESSFULLY!")
    return True

def create_simple_api_server():
    """Create a simple HTTP server for testing"""
    print("\n🌐 Starting Simple HTTP API Server...")
    
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class VaultAPIHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"status": "healthy", "service": "vault-api", "vault_path": VAULT_PATH}
                    self.wfile.write(json.dumps(response).encode())
                
                elif self.path == '/vault/stats':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    # Get vault stats
                    md_files = list(Path(VAULT_PATH).rglob("*.md"))
                    response = {
                        "vault_name": VAULT_NAME,
                        "total_files": len(md_files),
                        "vault_path": VAULT_PATH,
                        "sample_files": [str(f.relative_to(VAULT_PATH)) for f in md_files[:10]]
                    }
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'{"error": "Not found"}')
        
        server = HTTPServer(('localhost', 8082), VaultAPIHandler)
        print("✅ Server started at http://localhost:8082")
        print("📋 Available endpoints:")
        print("  • GET /health - Health check")
        print("  • GET /vault/stats - Vault statistics")
        print("\n🚀 Server running... Press Ctrl+C to stop")
        server.serve_forever()
        
    except ImportError:
        print("❌ HTTP server modules not available")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    # Run vault access test
    if test_vault_access():
        print("\n" + "="*60)
        choice = input("🌐 Start simple API server? (y/n): ").lower().strip()
        if choice == 'y':
            create_simple_api_server()
