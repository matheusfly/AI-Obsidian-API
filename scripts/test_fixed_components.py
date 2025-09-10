#!/usr/bin/env python3
"""
Test Fixed Components
"""

import sys
import os
import json
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_reranker():
    """Test ReRanker component"""
    print("🧪 Testing ReRanker...")
    try:
        from reranker import ReRanker
        
        reranker = ReRanker()
        query = "machine learning algorithms"
        candidates = [
            {
                "content": "Machine learning algorithms are powerful tools for data analysis.",
                "similarity": 0.8,
                "heading": "ML Introduction"
            },
            {
                "content": "Philosophical logic deals with reasoning and argumentation.",
                "similarity": 0.3,
                "heading": "Philosophy"
            }
        ]
        
        reranked = reranker.rerank(query, candidates, top_k=2)
        print(f"✅ ReRanker: {len(reranked)} results")
        return True
    except Exception as e:
        print(f"❌ ReRanker failed: {e}")
        return False

def test_topic_detector():
    """Test TopicDetector component"""
    print("🧪 Testing TopicDetector...")
    try:
        from topic_detector import TopicDetector
        
        detector = TopicDetector()
        query = "machine learning algorithms"
        topic = detector.detect_topic(query)
        print(f"✅ TopicDetector: {topic}")
        return True
    except Exception as e:
        print(f"❌ TopicDetector failed: {e}")
        return False

def test_smart_document_filter():
    """Test SmartDocumentFilter component"""
    print("🧪 Testing SmartDocumentFilter...")
    try:
        from smart_document_filter import SmartDocumentFilter
        from topic_detector import TopicDetector
        
        topic_detector = TopicDetector()
        filter_system = SmartDocumentFilter(topic_detector)
        
        documents = [
            {
                "content": "Machine learning algorithms are powerful tools.",
                "heading": "ML Introduction",
                "word_count": 8,
                "metadata": {
                    "topic": "technology",
                    "tags": ["ai", "ml"],
                    "file_type": "tutorial"
                }
            }
        ]
        
        filtered_docs = filter_system.smart_filter(documents, "machine learning", {})
        print(f"✅ SmartDocumentFilter: {len(filtered_docs)} results")
        return True
    except Exception as e:
        print(f"❌ SmartDocumentFilter failed: {e}")
        return False

def test_advanced_content_processor():
    """Test AdvancedContentProcessor component"""
    print("🧪 Testing AdvancedContentProcessor...")
    try:
        from advanced_content_processor import AdvancedContentProcessor
        
        processor = AdvancedContentProcessor()
        sample_content = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence.

## Types of ML

### Supervised Learning
Supervised learning uses labeled data.
"""
        
        chunks = processor.chunk_content(
            sample_content,
            {"title": "ML Guide", "topic": "technology"},
            "/test/ml_guide.md"
        )
        print(f"✅ AdvancedContentProcessor: {len(chunks)} chunks")
        return True
    except Exception as e:
        print(f"❌ AdvancedContentProcessor failed: {e}")
        return False

def test_validation_scripts():
    """Test validation scripts"""
    print("🧪 Testing ValidationScripts...")
    try:
        from validation_embedding_quality_fixed import EmbeddingQualityValidator
        
        validator = EmbeddingQualityValidator()
        test_text = "Machine learning is a subset of artificial intelligence"
        embedding = validator.generate_embedding(test_text)
        print(f"✅ ValidationScripts: embedding shape {embedding.shape}")
        return True
    except Exception as e:
        print(f"❌ ValidationScripts failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Fixed Components")
    print("=" * 40)
    
    tests = [
        test_reranker,
        test_topic_detector,
        test_smart_document_filter,
        test_advanced_content_processor,
        test_validation_scripts
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n📊 Test Results:")
    print(f"Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Most tests passed!")
    else:
        print("💥 Many tests failed!")
    
    # Save results
    with open("fixed_components_test_results.json", "w") as f:
        json.dump({
            "passed": passed,
            "total": total,
            "success_rate": success_rate,
            "results": results
        }, f, indent=2)
    
    print("📄 Results saved to fixed_components_test_results.json")

if __name__ == "__main__":
    main()
