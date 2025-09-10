#!/usr/bin/env python3
"""Test direct ChromaDB search without embedding function"""

import chromadb
from chromadb.utils import embedding_functions

def test_direct_search():
    # Connect to ChromaDB directly
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Get the collection
    collection = client.get_collection("enhanced_obsidian_vault")
    
    print(f"Collection count: {collection.count()}")
    
    # Try to query with text (this should fail if no embedding function)
    try:
        results = collection.query(
            query_texts=["performance optimization"],
            n_results=3
        )
        print(f"Text query successful: {len(results['documents'][0])} results")
    except Exception as e:
        print(f"Text query failed: {e}")
    
    # Try to get some documents to see what's in there
    try:
        all_docs = collection.get(limit=3)
        print(f"Direct get successful: {len(all_docs['documents'])} documents")
        for i, doc in enumerate(all_docs['documents'][:2]):
            print(f"Doc {i+1}: {doc[:100]}...")
    except Exception as e:
        print(f"Direct get failed: {e}")

if __name__ == "__main__":
    test_direct_search()
