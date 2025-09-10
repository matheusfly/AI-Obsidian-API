#!/usr/bin/env python3
"""Analyze file filtering in our data pipeline"""

from src.ingestion.filesystem_client import FilesystemVaultClient
import asyncio

async def analyze_filtering():
    client = FilesystemVaultClient('D:/Nomade Milionario')
    
    # Get all files that our client finds
    files = await client.list_vault_files()
    print(f'Files found by FilesystemVaultClient: {len(files)}')
    
    # Check vault stats
    stats = client.get_vault_stats()
    print(f'Vault stats total files: {stats["total_files"]}')
    print(f'Vault stats total size: {stats["total_size_mb"]} MB')
    
    # Show some examples
    print('\nFirst 5 files found:')
    for i, file in enumerate(files[:5]):
        print(f'  {file["path"]} ({file["size"]} bytes)')

if __name__ == "__main__":
    asyncio.run(analyze_filtering())
