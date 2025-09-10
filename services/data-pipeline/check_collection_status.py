#!/usr/bin/env python3
"""Check ChromaDB collection status"""

from src.vector.chroma_service import ChromaService

def check_collection():
    cs = ChromaService(collection_name='obsidian_vault')
    count = cs.collection.count()
    print(f'Collection count: {count}')
    
    if count > 0:
        sample = cs.collection.get(limit=1)
        if sample['metadatas']:
            print(f'Sample metadata keys: {list(sample["metadatas"][0].keys())}')
            print(f'Sample content preview: {sample["documents"][0][:100]}...')
        else:
            print('No metadata found')
    else:
        print('Collection is empty - need to ingest data first')

if __name__ == "__main__":
    check_collection()
