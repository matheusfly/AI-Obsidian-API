#!/usr/bin/env python3
"""Quick test to check search functionality with existing embeddings"""

from src.vector.chroma_service import ChromaService

def test_search():
    # Initialize ChromaService with the collection that has embeddings
    cs = ChromaService(collection_name='enhanced_obsidian_vault')
    
    print(f"Collection count: {cs.collection.count()}")
    
    # Test search
    query = "performance optimization"
    results = cs.search_similar(query, n_results=3)
    
    print(f"\nSearch query: '{query}'")
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"  Result keys: {list(result.keys())}")
        if 'similarity' in result:
            print(f"  Similarity: {result['similarity']:.3f}")
        if 'metadata' in result:
            print(f"  File: {result['metadata'].get('file_name', 'N/A')}")
            print(f"  Heading: {result['metadata'].get('heading', 'N/A')}")
        if 'content' in result:
            print(f"  Content preview: {result['content'][:100]}...")

if __name__ == "__main__":
    test_search()
