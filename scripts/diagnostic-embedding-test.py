#!/usr/bin/env python3
"""
Diagnostic test for embedding pipeline to identify 1.000 similarity score issue
"""

import sys
from pathlib import Path

def test_embedding_pipeline():
    """Test embedding pipeline to diagnose 1.000 similarity issue"""
    print("🔍 Diagnostic Test: Embedding Pipeline")
    print("=" * 50)
    
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        print("✅ Dependencies loaded successfully")
        
        # Test with different models
        models_to_test = [
            'all-MiniLM-L6-v2',
            'paraphrase-multilingual-MiniLM-L12-v2',
            'all-MiniLM-L12-v2'
        ]
        
        for model_name in models_to_test:
            print(f"\n🧪 Testing model: {model_name}")
            try:
                model = SentenceTransformer(model_name)
                
                # Test with clearly different texts
                test_texts = [
                    "Philosophy of mathematics deals with the nature of mathematical objects",
                    "Web scraping with Scrapy requires understanding of HTML and CSS selectors", 
                    "High performance reading techniques improve comprehension speed",
                    "Machine learning algorithms use neural networks for pattern recognition",
                    "Business strategy development involves market analysis and competitive positioning"
                ]
                
                print(f"   📝 Testing with {len(test_texts)} different texts...")
                
                # Generate embeddings
                embeddings = model.encode(test_texts)
                print(f"   📊 Embedding shape: {embeddings.shape}")
                
                # Calculate similarity matrix
                similarity_matrix = cosine_similarity(embeddings)
                
                print("   📈 Similarity Matrix:")
                for i in range(len(test_texts)):
                    for j in range(i+1, len(test_texts)):
                        similarity = similarity_matrix[i][j]
                        print(f"      Text {i+1} vs Text {j+1}: {similarity:.3f}")
                
                # Check for problematic similarities
                problematic_similarities = []
                for i in range(len(test_texts)):
                    for j in range(i+1, len(test_texts)):
                        similarity = similarity_matrix[i][j]
                        if abs(similarity - 1.0) < 0.001:
                            problematic_similarities.append((i, j, similarity))
                
                if problematic_similarities:
                    print(f"   ⚠️  PROBLEM DETECTED: {len(problematic_similarities)} pairs with similarity ~1.0")
                    for i, j, sim in problematic_similarities:
                        print(f"      Text {i+1} vs Text {j+1}: {sim:.6f}")
                else:
                    print("   ✅ No problematic similarities detected")
                
                # Test with identical texts (should be 1.0)
                identical_texts = ["Test text", "Test text", "Test text"]
                identical_embeddings = model.encode(identical_texts)
                identical_similarity = cosine_similarity([identical_embeddings[0]], [identical_embeddings[1]])[0][0]
                print(f"   🔍 Identical text similarity: {identical_similarity:.6f}")
                
                if abs(identical_similarity - 1.0) > 0.001:
                    print("   ⚠️  WARNING: Identical texts don't have similarity 1.0")
                else:
                    print("   ✅ Identical texts correctly show similarity 1.0")
                
            except Exception as e:
                print(f"   ❌ Error testing {model_name}: {e}")
        
        print("\n🎯 Diagnostic Summary:")
        print("   - If you see similarities ~1.0 for different texts, the model is broken")
        print("   - If you see realistic similarities (0.1-0.8), the model is working")
        print("   - Check your embedding generation code for bugs")
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Install with: pip install sentence-transformers scikit-learn")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_vector_database():
    """Test vector database functionality"""
    print("\n🔍 Diagnostic Test: Vector Database")
    print("=" * 50)
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        print("✅ ChromaDB imported successfully")
        
        # Create test client
        client = chromadb.PersistentClient(path="./test_chroma")
        collection = client.create_collection("diagnostic_test")
        
        print("✅ Test collection created")
        
        # Add test documents
        test_documents = [
            "Philosophy of mathematics and logical reasoning",
            "Web development with Python and Django", 
            "Machine learning algorithms and neural networks",
            "Business strategy and market analysis",
            "Performance optimization techniques"
        ]
        
        test_metadatas = [
            {"topic": "philosophy", "type": "academic"},
            {"topic": "programming", "type": "technical"},
            {"topic": "ai", "type": "technical"},
            {"topic": "business", "type": "strategy"},
            {"topic": "performance", "type": "technical"}
        ]
        
        test_ids = [f"doc_{i+1}" for i in range(len(test_documents))]
        
        collection.add(
            documents=test_documents,
            metadatas=test_metadatas,
            ids=test_ids
        )
        
        print("✅ Test documents added")
        
        # Test search
        test_queries = [
            "mathematical logic and philosophy",
            "Python web development",
            "neural networks and machine learning",
            "business strategy development",
            "performance optimization"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            print("   📊 Results:")
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                similarity = 1 - distance
                print(f"      {i+1}. Similarity: {similarity:.3f} - {doc[:50]}...")
                
                # Check for problematic similarities
                if abs(similarity - 1.0) < 0.001:
                    print(f"         ⚠️  PROBLEM: Similarity too close to 1.0")
        
        print("\n✅ Vector database test completed")
        
    except ImportError as e:
        print(f"❌ Missing ChromaDB: {e}")
        print("   Install with: pip install chromadb")
    except Exception as e:
        print(f"❌ Vector database error: {e}")

if __name__ == "__main__":
    test_embedding_pipeline()
    test_vector_database()
