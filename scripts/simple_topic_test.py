#!/usr/bin/env python3
"""
Simple test for TopicDetector
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing TopicDetector import...")
    from topic_detector import TopicDetector
    print("✅ Import successful")
    
    print("Testing initialization...")
    detector = TopicDetector()
    print("✅ Initialization successful")
    
    print("Testing topic detection...")
    query = "machine learning algorithms"
    topic = detector.detect_topic(query)
    print(f"✅ Topic detection successful: '{query}' -> {topic}")
    
    print("Testing multiple topics...")
    topics = detector.detect_multiple_topics(query)
    print(f"✅ Multiple topics successful: {topics}")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
