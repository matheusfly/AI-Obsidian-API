#!/usr/bin/env python3
"""
Phase 1.1: Real Embedding Service Validation
Tests embedding quality with real vault data
"""

import sys
import time
import json
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# Add data-pipeline src to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

def test_embedding_quality_with_real_data():
    """Test embedding quality using real vault data"""
    print("🧪 Phase 1.1: Real Embedding Service Quality Test")
    print("=" * 60)
    
    try:
        from embeddings.embedding_service import EmbeddingService
        
        # Initialize service
        embedding_service = EmbeddingService(
            model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        
        # Load real vault data
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        vault_files = list(vault_path.glob("*.md"))
        
        if not vault_files:
            print("❌ No vault files found")
            return {"error": "No vault files", "passed": False}
        
        # Read real content
        real_contents = []
        for file_path in vault_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    real_contents.append({
                        "file": file_path.name,
                        "content": content,
                        "word_count": len(content.split()),
                        "char_count": len(content)
                    })
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        if len(real_contents) < 2:
            print("❌ Need at least 2 files for similarity testing")
            return {"error": "Insufficient files", "passed": False}
        
        print(f"📚 Testing with {len(real_contents)} real vault files")
        
        # Test 1: Semantic Similarity Validation
        print("\n🔍 Test 1: Semantic Similarity Validation")
        similarity_results = []
        
        for i in range(len(real_contents)):
            for j in range(i + 1, len(real_contents)):
                content1 = real_contents[i]["content"]
                content2 = real_contents[j]["content"]
                
                # Generate embeddings
                emb1 = embedding_service.generate_embedding(content1)
                emb2 = embedding_service.generate_embedding(content2)
                
                # Calculate similarity
                similarity = cosine_similarity([emb1], [emb2])[0][0]
                
                similarity_results.append({
                    "file1": real_contents[i]["file"],
                    "file2": real_contents[j]["file"],
                    "similarity": float(similarity),
                    "word_count1": real_contents[i]["word_count"],
                    "word_count2": real_contents[j]["word_count"]
                })
        
        # Analyze similarity distribution
        similarities = [r["similarity"] for r in similarity_results]
        avg_similarity = np.mean(similarities)
        min_similarity = np.min(similarities)
        max_similarity = np.max(similarities)
        std_similarity = np.std(similarities)
        
        print(f"  Average Similarity: {avg_similarity:.3f}")
        print(f"  Min Similarity: {min_similarity:.3f}")
        print(f"  Max Similarity: {max_similarity:.3f}")
        print(f"  Std Deviation: {std_similarity:.3f}")
        
        # Test 2: Consistency Validation
        print("\n🔄 Test 2: Consistency Validation")
        consistency_results = []
        
        for content in real_contents[:3]:  # Test first 3 files
            # Generate embedding twice
            emb1 = embedding_service.generate_embedding(content["content"])
            emb2 = embedding_service.generate_embedding(content["content"])
            
            consistency = cosine_similarity([emb1], [emb2])[0][0]
            consistency_results.append({
                "file": content["file"],
                "consistency": float(consistency)
            })
        
        avg_consistency = np.mean([r["consistency"] for r in consistency_results])
        print(f"  Average Consistency: {avg_consistency:.3f}")
        
        # Test 3: Dimensionality Validation
        print("\n📏 Test 3: Dimensionality Validation")
        test_embedding = embedding_service.generate_embedding("Test content for dimensionality validation")
        embedding_dim = len(test_embedding)
        print(f"  Embedding Dimension: {embedding_dim}")
        
        # Test 4: Multilingual Capability
        print("\n🌍 Test 4: Multilingual Capability")
        multilingual_tests = [
            ("English: Machine learning algorithms", "English: Artificial intelligence systems"),
            ("Portuguese: Algoritmos de aprendizado de máquina", "Portuguese: Sistemas de inteligência artificial"),
            ("English: Machine learning", "Portuguese: Aprendizado de máquina")
        ]
        
        multilingual_results = []
        for text1, text2 in multilingual_tests:
            emb1 = embedding_service.generate_embedding(text1)
            emb2 = embedding_service.generate_embedding(text2)
            similarity = cosine_similarity([emb1], [emb2])[0][0]
            
            multilingual_results.append({
                "text1": text1,
                "text2": text2,
                "similarity": float(similarity)
            })
        
        avg_multilingual_similarity = np.mean([r["similarity"] for r in multilingual_results])
        print(f"  Average Multilingual Similarity: {avg_multilingual_similarity:.3f}")
        
        # Quality Assessment
        quality_checks = {
            "semantic_diversity": 0.1 < avg_similarity < 0.8,  # Not too similar, not too different
            "consistency": avg_consistency > 0.99,  # Very high consistency
            "dimensionality": embedding_dim == 384,  # Expected dimension
            "multilingual": avg_multilingual_similarity > 0.3  # Some cross-language similarity
        }
        
        passed_checks = sum(quality_checks.values())
        total_checks = len(quality_checks)
        quality_score = passed_checks / total_checks
        
        print(f"\n📊 Quality Assessment")
        print(f"  Semantic Diversity: {'✅' if quality_checks['semantic_diversity'] else '❌'}")
        print(f"  Consistency: {'✅' if quality_checks['consistency'] else '❌'}")
        print(f"  Dimensionality: {'✅' if quality_checks['dimensionality'] else '❌'}")
        print(f"  Multilingual: {'✅' if quality_checks['multilingual'] else '❌'}")
        print(f"  Quality Score: {quality_score:.2%}")
        
        results = {
            "test_name": "Phase 1.1 Real Embedding Service Quality Test",
            "passed": quality_score >= 0.75,
            "quality_score": quality_score,
            "embedding_dimension": embedding_dim,
            "model_name": embedding_service.model_name,
            "multilingual": embedding_service.is_multilingual,
            "files_tested": len(real_contents),
            "similarity_stats": {
                "average": avg_similarity,
                "min": min_similarity,
                "max": max_similarity,
                "std": std_similarity
            },
            "consistency_stats": {
                "average": avg_consistency
            },
            "multilingual_stats": {
                "average": avg_multilingual_similarity
            },
            "quality_checks": quality_checks,
            "similarity_results": similarity_results,
            "consistency_results": consistency_results,
            "multilingual_results": multilingual_results
        }
        
        print(f"\n🎯 Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "passed": False}

if __name__ == "__main__":
    results = test_embedding_quality_with_real_data()
    
    # Save results
    with open("phase1_embedding_real_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nFinal Result: {'✅ PASS' if results.get('passed', False) else '❌ FAIL'}")
