#!/usr/bin/env python3
"""
Simple test to verify Python execution
"""

print("🧪 Simple Validation Test")
print("=" * 30)

try:
    import numpy as np
    print("✅ NumPy imported successfully")
    
    # Test basic functionality
    test_vector = np.array([1, 2, 3, 4, 5])
    norm = np.linalg.norm(test_vector)
    print(f"✅ NumPy norm calculation: {norm:.3f}")
    
    # Test cosine similarity
    vec1 = np.array([1, 0, 0])
    vec2 = np.array([0, 1, 0])
    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    print(f"✅ Cosine similarity test: {similarity:.3f}")
    
    print("\n🎯 All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
