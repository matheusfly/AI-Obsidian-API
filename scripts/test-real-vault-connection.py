#!/usr/bin/env python3
"""
Test Real Vault Connection
Quick test to verify connection to D:/Nomade Milionario
"""

import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_vault_connection():
    """Test connection to real vault"""
    logger.info("🔍 Testing Real Vault Connection")
    logger.info("=" * 40)
    
    # Real vault path
    real_vault_path = Path(r"D:\Nomade Milionario")
    
    logger.info(f"📚 Real vault path: {real_vault_path}")
    logger.info(f"📁 Exists: {real_vault_path.exists()}")
    
    if not real_vault_path.exists():
        logger.error("❌ Real vault not found!")
        return False
    
    # Scan for markdown files
    logger.info("🔍 Scanning for markdown files...")
    markdown_files = list(real_vault_path.rglob("*.md"))
    
    logger.info(f"📄 Found {len(markdown_files)} markdown files")
    
    if markdown_files:
        logger.info("📄 Sample files:")
        for i, file_path in enumerate(markdown_files[:10]):
            logger.info(f"  {i+1}. {file_path.name}")
        
        if len(markdown_files) > 10:
            logger.info(f"  ... and {len(markdown_files) - 10} more files")
        
        # Test reading a file
        test_file = markdown_files[0]
        logger.info(f"\n📖 Testing file: {test_file.name}")
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"✅ File read successfully")
            logger.info(f"📊 Content length: {len(content)} characters")
            logger.info(f"📝 First 200 chars: {content[:200]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reading file: {e}")
            return False
    
    else:
        logger.warning("⚠️ No markdown files found")
        return False

def main():
    """Main function"""
    success = test_real_vault_connection()
    
    if success:
        logger.info("\n🎉 Real vault connection test PASSED!")
        logger.info("✅ Ready to proceed with RAG system")
    else:
        logger.error("\n❌ Real vault connection test FAILED!")
        logger.error("Please check the vault path and permissions")

if __name__ == "__main__":
    main()
