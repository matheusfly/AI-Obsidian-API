#!/usr/bin/env python3
"""
Simple test for validation scripts
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing validation_embedding_quality import...")
    from validation_embedding_quality import EmbeddingQualityValidator
    print("✅ Import successful")
    
    print("Testing initialization...")
    validator = EmbeddingQualityValidator()
    print("✅ Initialization successful")
    
    print("Testing embedding generation...")
    test_text = "Machine learning is a subset of artificial intelligence"
    embedding = validator.generate_embedding(test_text)
    print(f"✅ Embedding generated: shape {embedding.shape}")
    
    print("Testing embedding quality...")
    results = validator.test_embedding_quality()
    print(f"✅ Quality test completed: {results['overall_score']:.1%} success rate")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
