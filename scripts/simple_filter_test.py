#!/usr/bin/env python3
"""
Simple test for SmartDocumentFilter
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing SmartDocumentFilter import...")
    from smart_document_filter import SmartDocumentFilter
    print("✅ Import successful")
    
    print("Testing TopicDetector import...")
    from topic_detector import TopicDetector
    print("✅ TopicDetector import successful")
    
    print("Testing initialization...")
    topic_detector = TopicDetector()
    filter_system = SmartDocumentFilter(topic_detector)
    print("✅ Initialization successful")
    
    print("Testing basic filtering...")
    sample_docs = [
        {
            "content": "Machine learning algorithms are powerful tools for data analysis.",
            "heading": "ML Introduction",
            "word_count": 10,
            "metadata": {
                "topic": "technology",
                "tags": ["ai", "ml"],
                "file_type": "tutorial"
            }
        },
        {
            "content": "Philosophical logic deals with reasoning and argumentation.",
            "heading": "Philosophy",
            "word_count": 8,
            "metadata": {
                "topic": "philosophy",
                "tags": ["logic"],
                "file_type": "academic"
            }
        }
    ]
    
    # Test topic filtering
    tech_docs = filter_system.filter_by_topic(sample_docs, "technology")
    print(f"✅ Topic filtering: {len(tech_docs)} tech documents found")
    
    # Test smart filtering
    filtered_docs = filter_system.smart_filter(sample_docs, "machine learning", {})
    print(f"✅ Smart filtering: {len(filtered_docs)} documents found")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
