#!/usr/bin/env python3
"""Test manual embedding storage and search"""

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService

def test_manual_embeddings():
    # Initialize services
    chroma_service = ChromaService(
        persist_directory="./chroma_db",
        collection_name="enhanced_obsidian_vault",
        embedding_model="all-MiniLM-L6-v2"
    )
    
    embedding_service = EmbeddingService()
    
    print(f"Collection count before: {chroma_service.collection.count()}")
    
    # Create test data
    test_chunks = [
        {
            "content": "This is a test document about performance optimization techniques.",
            "path": "test_performance.md",
            "heading": "Performance Optimization",
            "chunk_index": 0,
            "file_metadata": {
                "word_count": 10,
                "char_count": 60,
                "size": 60,
                "modified": 1234567890,
                "created": 1234567890,
                "frontmatter": {"tags": ["performance", "optimization"]},
                "in_content_tags": []
            }
        },
        {
            "content": "Machine learning algorithms can be optimized for better performance.",
            "path": "test_ml.md", 
            "heading": "ML Optimization",
            "chunk_index": 0,
            "file_metadata": {
                "word_count": 8,
                "char_count": 65,
                "size": 65,
                "modified": 1234567890,
                "created": 1234567890,
                "frontmatter": {"tags": ["machine-learning", "algorithms"]},
                "in_content_tags": []
            }
        }
    ]
    
    # Generate embeddings
    texts = [chunk["content"] for chunk in test_chunks]
    embeddings = [embedding_service.generate_embedding(text) for text in texts]
    
    print(f"Generated {len(embeddings)} embeddings")
    
    # Store embeddings
    chroma_service.store_embeddings(test_chunks, embeddings)
    
    print(f"Collection count after: {chroma_service.collection.count()}")
    
    # Test search
    results = chroma_service.search_similar("performance optimization", n_results=2)
    print(f"Search results: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"Result {i+1}:")
        print(f"  Similarity: {result['similarity_score']:.3f}")
        print(f"  Content: {result['content'][:50]}...")

if __name__ == "__main__":
    test_manual_embeddings()
