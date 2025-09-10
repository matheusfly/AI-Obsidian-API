#!/usr/bin/env python3
"""
Test that writes output to a file
"""

import sys
from pathlib import Path

# Create output file
output_file = Path("test_output.txt")

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("🧪 Simple Validation Test\n")
        f.write("=" * 30 + "\n")
        
        try:
            import numpy as np
            f.write("✅ NumPy imported successfully\n")
            
            # Test basic functionality
            test_vector = np.array([1, 2, 3, 4, 5])
            norm = np.linalg.norm(test_vector)
            f.write(f"✅ NumPy norm calculation: {norm:.3f}\n")
            
            # Test cosine similarity
            vec1 = np.array([1, 0, 0])
            vec2 = np.array([0, 1, 0])
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            f.write(f"✅ Cosine similarity test: {similarity:.3f}\n")
            
            f.write("\n🎯 All basic tests passed!\n")
            
        except Exception as e:
            f.write(f"❌ Error: {e}\n")
            import traceback
            f.write(traceback.format_exc())
    
    print(f"Test completed. Check {output_file} for results.")
    
except Exception as e:
    print(f"Failed to create test file: {e}")
