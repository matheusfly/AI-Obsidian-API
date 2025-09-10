#!/usr/bin/env python3
"""
Simple working test to verify Python environment
"""

import sys
import os
import json
import time

print("🚀 Starting Simple Working Test")
print("=" * 40)

# Test basic Python functionality
print("✅ Python is working")

# Test imports
try:
    import numpy as np
    print("✅ NumPy imported successfully")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")

try:
    import sklearn
    print("✅ Scikit-learn imported successfully")
except ImportError as e:
    print(f"❌ Scikit-learn import failed: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ SentenceTransformers imported successfully")
except ImportError as e:
    print(f"❌ SentenceTransformers import failed: {e}")

# Test file operations
test_data = {
    "test": "data",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "python_version": sys.version
}

try:
    with open("simple_test_output.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2)
    print("✅ File operations working")
except Exception as e:
    print(f"❌ File operations failed: {e}")

# Test basic functionality
try:
    # Test simple embedding generation
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    test_text = "This is a test sentence for embedding generation"
    embedding = model.encode(test_text)
    print(f"✅ Embedding generation working: shape {embedding.shape}")
except Exception as e:
    print(f"❌ Embedding generation failed: {e}")

print("\n🎉 Simple Working Test Completed!")
print("=" * 40)
