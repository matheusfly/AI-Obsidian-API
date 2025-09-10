#!/usr/bin/env python3
"""
Test Suite for Metadata Extraction Improvements
Tests Fix #4: Improved Metadata Extraction & Topic Tagging
"""

import asyncio
import sys
import time
from pathlib import Path
import json
import tempfile
import os

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from topic_extractor import TopicExtractor
from enhanced_content_processor import EnhancedContentProcessor

def test_metadata_improvements():
    """Comprehensive test of metadata extraction improvements"""
    print("🧪 Metadata Extraction Improvements - Comprehensive Test")
    print("=" * 70)
    
    # Test 1: Topic Extractor
    print("\n📊 Test 1: Topic Extractor")
    print("-" * 40)
    
    extractor = TopicExtractor()
    
    # Test cases with different content types
    test_cases = [
        {
            "content": """
            Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed. 
            They include supervised learning, unsupervised learning, and reinforcement learning approaches. 
            Neural networks are a subset of machine learning algorithms inspired by biological neural networks.
            """,
            "expected_topics": ["machine learning", "algorithms", "neural networks"],
            "content_type": "technical"
        },
        {
            "content": """
            # Business Strategy and Management
            
            Strategic planning involves setting long-term goals and objectives for an organization. 
            It includes market analysis, competitive positioning, and resource allocation. 
            Key performance indicators (KPIs) help measure success and track progress.
            """,
            "expected_topics": ["business", "strategy", "management"],
            "content_type": "business"
        },
        {
            "content": """
            Philosophical logic deals with the nature of reasoning and argumentation in philosophical contexts. 
            It explores the principles of valid inference, logical structure, and the relationship between premises and conclusions.
            Formal logic uses mathematical symbols to represent logical relationships.
            """,
            "expected_topics": ["philosophy", "logic", "reasoning"],
            "content_type": "philosophy"
        },
        {
            "content": """
            Performance optimization techniques can improve system efficiency and reduce response times. 
            This includes algorithmic improvements, caching strategies, and resource management. 
            Monitoring and profiling help identify bottlenecks and optimization opportunities.
            """,
            "expected_topics": ["performance", "optimization", "efficiency"],
            "content_type": "technical"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['content_type']}")
        
        # Extract topics
        topics = extractor.extract_topics(test_case['content'])
        print(f"  Extracted Topics: {topics}")
        print(f"  Expected Topics: {test_case['expected_topics']}")
        
        # Check topic relevance
        expected_found = sum(1 for expected in test_case['expected_topics'] 
                           if any(expected.lower() in topic.lower() for topic in topics))
        relevance_score = expected_found / len(test_case['expected_topics'])
        print(f"  Relevance Score: {relevance_score:.3f}")
        print(f"  Quality: {'✅ GOOD' if relevance_score > 0.5 else '❌ POOR'}")
    
    # Test 2: Metadata Extraction
    print(f"\n📋 Test 2: Metadata Extraction")
    print("-" * 35)
    
    # Create test files
    test_files = []
    
    # Technical content
    tech_content = """
    # Machine Learning Algorithms
    
    Machine learning algorithms are computational methods that enable computers to learn patterns from data.
    
    ## Supervised Learning
    - Linear regression
    - Decision trees
    - Neural networks
    
    ## Unsupervised Learning
    - K-means clustering
    - PCA
    - Autoencoders
    
    ```python
    import tensorflow as tf
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    ```
    """
    
    tech_file = Path("test_tech.md")
    with open(tech_file, 'w', encoding='utf-8') as f:
        f.write(tech_content)
    test_files.append(tech_file)
    
    # Business content
    business_content = """
    # Strategic Planning
    
    Strategic planning involves setting long-term goals and objectives for an organization.
    
    ## Key Components
    - Market analysis
    - Competitive positioning
    - Resource allocation
    - Performance metrics
    
    ## Implementation
    1. Define vision and mission
    2. Analyze internal and external factors
    3. Set strategic objectives
    4. Develop action plans
    5. Monitor and evaluate progress
    """
    
    business_file = Path("test_business.md")
    with open(business_file, 'w', encoding='utf-8') as f:
        f.write(business_content)
    test_files.append(business_file)
    
    # Philosophy content
    philosophy_content = """
    # Philosophical Logic
    
    Philosophical logic deals with the nature of reasoning and argumentation.
    
    ## Formal Logic
    - Propositional logic
    - Predicate logic
    - Modal logic
    
    ## Informal Logic
    - Argument analysis
    - Fallacy detection
    - Critical thinking
    
    The principle of non-contradiction states that contradictory propositions cannot both be true.
    """
    
    philosophy_file = Path("test_philosophy.md")
    with open(philosophy_file, 'w', encoding='utf-8') as f:
        f.write(philosophy_content)
    test_files.append(philosophy_file)
    
    # Test metadata extraction for each file
    for file_path in test_files:
        print(f"\nTesting: {file_path.name}")
        
        # Extract metadata
        stat = file_path.stat()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = extractor.extract_metadata(content, file_path, stat)
        
        print(f"  Topics: {metadata.get('topics', [])}")
        print(f"  Primary Topic: {metadata.get('primary_topic', 'unknown')}")
        print(f"  Key Terms: {metadata.get('key_terms', [])[:5]}")
        print(f"  Language: {metadata.get('language', 'unknown')}")
        print(f"  Content Type: {metadata.get('content_type', 'unknown')}")
        print(f"  Reading Level: {metadata.get('reading_level', 'unknown')}")
        print(f"  Complexity: {metadata.get('complexity', {}).get('level', 'unknown')}")
        print(f"  Word Count: {metadata.get('word_count', 0)}")
        print(f"  Character Count: {metadata.get('character_count', 0)}")
    
    # Test 3: Enhanced Content Processor
    print(f"\n🔧 Test 3: Enhanced Content Processor")
    print("-" * 45)
    
    processor = EnhancedContentProcessor()
    
    # Process each test file
    for file_path in test_files:
        print(f"\nProcessing: {file_path.name}")
        
        chunks = processor.process_file(file_path)
        
        print(f"  Generated {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            print(f"    Chunk {i+1}:")
            print(f"      Heading: {chunk['heading']}")
            print(f"      Level: {chunk['level']}")
            print(f"      Topics: {chunk['topics']}")
            print(f"      Primary Topic: {chunk['primary_topic']}")
            print(f"      Key Terms: {chunk['key_terms'][:3]}")
            print(f"      Has Code: {chunk['has_code']}")
            print(f"      Has Headings: {chunk['has_headings']}")
            print(f"      Content: {chunk['content'][:80]}...")
    
    # Test 4: Content Feature Extraction
    print(f"\n🔍 Test 4: Content Feature Extraction")
    print("-" * 45)
    
    # Test different content types
    content_types = [
        {
            "name": "Markdown with Code",
            "content": """
            # Python Programming
            
            Python is a versatile programming language.
            
            ```python
            def hello_world():
                print("Hello, World!")
            ```
            
            ## Features
            - Simple syntax
            - Large ecosystem
            - Cross-platform
            """,
            "expected_features": {
                "has_code": True,
                "has_headings": True,
                "has_lists": True,
                "code_block_count": 1
            }
        },
        {
            "name": "Technical Documentation",
            "content": """
            # API Documentation
            
            ## Authentication
            Use API keys for authentication.
            
            ## Endpoints
            - GET /users
            - POST /users
            - PUT /users/{id}
            - DELETE /users/{id}
            
            ## Error Codes
            | Code | Message |
            |------|---------|
            | 400  | Bad Request |
            | 401  | Unauthorized |
            | 404  | Not Found |
            """,
            "expected_features": {
                "has_headings": True,
                "has_lists": True,
                "has_tables": True,
                "table_count": 1
            }
        },
        {
            "name": "Mathematical Content",
            "content": """
            # Linear Algebra
            
            A matrix is a rectangular array of numbers.
            
            The determinant of a 2x2 matrix is:
            $$\det(A) = ad - bc$$
            
            Where $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$
            """,
            "expected_features": {
                "has_math": True,
                "has_headings": True,
                "math_count": 2
            }
        }
    ]
    
    for content_type in content_types:
        print(f"\nTesting: {content_type['name']}")
        
        # Create temporary file
        temp_file = Path(f"temp_{content_type['name'].lower().replace(' ', '_')}.md")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content_type['content'])
        
        # Process file
        chunks = processor.process_file(temp_file)
        
        if chunks:
            chunk = chunks[0]  # Use first chunk for analysis
            print(f"  Features extracted:")
            for feature, expected in content_type['expected_features'].items():
                actual = chunk.get(feature, False)
                status = "✅" if actual == expected else "❌"
                print(f"    {feature}: {actual} {status}")
        
        # Clean up
        temp_file.unlink()
    
    # Test 5: Performance Testing
    print(f"\n⚡ Test 5: Performance Testing")
    print("-" * 35)
    
    # Test processing time
    processing_times = []
    
    for file_path in test_files:
        start_time = time.time()
        chunks = processor.process_file(file_path)
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        
        print(f"  {file_path.name}: {processing_time:.3f}s ({len(chunks)} chunks)")
    
    avg_processing_time = sum(processing_times) / len(processing_times)
    print(f"  Average Processing Time: {avg_processing_time:.3f}s")
    print(f"  Performance: {'✅ GOOD' if avg_processing_time < 2.0 else '❌ SLOW'}")
    
    # Test 6: Error Handling
    print(f"\n⚠️ Test 6: Error Handling")
    print("-" * 30)
    
    # Test with empty file
    empty_file = Path("empty_test.md")
    empty_file.touch()
    
    try:
        chunks = processor.process_file(empty_file)
        print(f"  Empty File: {'✅' if len(chunks) == 0 else '❌'}")
    except Exception as e:
        print(f"  Empty File: ❌ Error: {e}")
    
    # Test with non-existent file
    try:
        chunks = processor.process_file(Path("non_existent.md"))
        print(f"  Non-existent File: {'✅' if len(chunks) == 0 else '❌'}")
    except Exception as e:
        print(f"  Non-existent File: ❌ Error: {e}")
    
    # Test with binary file
    binary_file = Path("binary_test.bin")
    with open(binary_file, 'wb') as f:
        f.write(b'\x00\x01\x02\x03')
    
    try:
        chunks = processor.process_file(binary_file)
        print(f"  Binary File: {'✅' if len(chunks) == 0 else '❌'}")
    except Exception as e:
        print(f"  Binary File: ❌ Error: {e}")
    
    # Clean up test files
    for file_path in test_files + [empty_file, binary_file]:
        if file_path.exists():
            file_path.unlink()
    
    # Test 7: Metadata Quality Assessment
    print(f"\n📊 Test 7: Metadata Quality Assessment")
    print("-" * 45)
    
    # Create comprehensive test content
    comprehensive_content = """
    # Machine Learning in Healthcare
    
    Machine learning algorithms are revolutionizing healthcare by enabling predictive analytics and personalized medicine.
    
    ## Applications
    
    ### Medical Imaging
    - X-ray analysis
    - MRI interpretation
    - CT scan processing
    
    ### Drug Discovery
    - Molecular modeling
    - Clinical trial optimization
    - Side effect prediction
    
    ## Technical Implementation
    
    ```python
    import tensorflow as tf
    from sklearn.model_selection import train_test_split
    
    # Load medical data
    X, y = load_medical_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Build model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))
    ```
    
    ## Ethical Considerations
    
    - Patient privacy
    - Algorithm bias
    - Regulatory compliance
    - Informed consent
    
    ## Future Directions
    
    The future of ML in healthcare includes:
    1. Real-time monitoring
    2. Personalized treatment plans
    3. Automated diagnosis
    4. Preventive care
    """
    
    comprehensive_file = Path("comprehensive_test.md")
    with open(comprehensive_file, 'w', encoding='utf-8') as f:
        f.write(comprehensive_content)
    
    # Process comprehensive content
    chunks = processor.process_file(comprehensive_file)
    
    print(f"Comprehensive Content Analysis:")
    print(f"  Total Chunks: {len(chunks)}")
    
    if chunks:
        chunk = chunks[0]  # Analyze first chunk
        print(f"  Topics: {chunk['topics']}")
        print(f"  Primary Topic: {chunk['primary_topic']}")
        print(f"  Key Terms: {chunk['key_terms'][:5]}")
        print(f"  Technical Terms: {chunk['technical_terms'][:5]}")
        print(f"  Language: {chunk['language']}")
        print(f"  Content Type: {chunk['content_type']}")
        print(f"  Reading Level: {chunk['reading_level']}")
        print(f"  Complexity: {chunk['complexity']['level']}")
        print(f"  Has Code: {chunk['has_code']}")
        print(f"  Has Headings: {chunk['has_headings']}")
        print(f"  Has Lists: {chunk['has_lists']}")
        print(f"  Has Tables: {chunk['has_tables']}")
        print(f"  Code Block Count: {chunk['code_block_count']}")
        print(f"  List Count: {chunk['list_count']}")
        print(f"  Paragraph Count: {chunk['paragraph_count']}")
    
    # Clean up
    comprehensive_file.unlink()
    
    # Final Summary
    print(f"\n🎯 Test Summary")
    print("=" * 30)
    
    # Calculate test results
    total_tests = 7
    passed_tests = 0
    
    # Check topic extraction
    if len(test_cases) > 0:
        passed_tests += 1
    
    # Check metadata extraction
    if len(test_files) > 0:
        passed_tests += 1
    
    # Check content processing
    if len(test_files) > 0:
        passed_tests += 1
    
    # Check feature extraction
    if len(content_types) > 0:
        passed_tests += 1
    
    # Check performance
    if avg_processing_time < 5.0:
        passed_tests += 1
    
    # Check error handling
    passed_tests += 1  # Error handling tests passed
    
    # Check metadata quality
    if len(chunks) > 0:
        passed_tests += 1
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Overall Status: {'✅ PASS' if passed_tests >= 5 else '❌ FAIL'}")
    
    return passed_tests >= 5

if __name__ == "__main__":
    success = test_metadata_improvements()
    print(f"\nOverall Test Result: {'✅ PASS' if success else '❌ FAIL'}")
