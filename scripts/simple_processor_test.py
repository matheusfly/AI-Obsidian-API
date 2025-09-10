#!/usr/bin/env python3
"""
Simple test for AdvancedContentProcessor
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing AdvancedContentProcessor import...")
    from advanced_content_processor import AdvancedContentProcessor
    print("✅ Import successful")
    
    print("Testing initialization...")
    processor = AdvancedContentProcessor()
    print("✅ Initialization successful")
    
    print("Testing content chunking...")
    sample_content = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.

## Types of Machine Learning

### Supervised Learning
Supervised learning uses labeled training data to learn a mapping from inputs to outputs.

### Unsupervised Learning
Unsupervised learning finds hidden patterns in data without labeled examples.

## Applications

Machine learning has applications in:
- Computer vision
- Natural language processing
- Recommendation systems
- Predictive analytics

# Conclusion

Machine learning is transforming how we approach complex problems in technology.
"""
    
    chunks = processor.chunk_content(
        sample_content, 
        {"title": "ML Guide", "topic": "technology"}, 
        "/test/ml_guide.md"
    )
    
    print(f"✅ Content chunking: Generated {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
        print(f"  Chunk {i+1}: {chunk['heading']} ({chunk['word_count']} words)")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
