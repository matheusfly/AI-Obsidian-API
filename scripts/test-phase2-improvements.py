#!/usr/bin/env python3
"""
Comprehensive Test Suite for Phase 2 RAG Improvements
Tests advanced chunking, topic detection, smart filtering, and re-ranking
"""

import asyncio
import sys
import time
from pathlib import Path
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from enhanced_agentic_rag_cli import EnhancedAgenticRAGCLI
from topic_detector import TopicDetector
from smart_document_filter import SmartDocumentFilter
from reranker import ReRanker
from advanced_content_processor import AdvancedContentProcessor
from rag_quality_validator import RAGQualityValidator

async def test_phase2_improvements():
    """Comprehensive test of all Phase 2 improvements"""
    print("🧪 Phase 2 RAG Improvements - Comprehensive Test")
    print("=" * 70)
    
    # Initialize all components
    print("🔧 Initializing components...")
    cli = EnhancedAgenticRAGCLI()
    topic_detector = TopicDetector()
    smart_filter = SmartDocumentFilter(topic_detector)
    reranker = ReRanker()
    content_processor = AdvancedContentProcessor()
    quality_validator = RAGQualityValidator()
    
    print(f"✅ All components initialized successfully")
    print(f"📊 System loaded {len(cli.documents)} document chunks")
    
    # Test 1: Topic Detection
    print(f"\n🧠 Test 1: Topic Detection")
    print("-" * 30)
    
    test_queries = [
        "philosophical logic and mathematical reasoning",
        "machine learning algorithms and neural networks", 
        "performance optimization and system efficiency",
        "business strategy and management techniques",
        "scientific research methods and experimentation"
    ]
    
    for query in test_queries:
        primary_topic = topic_detector.detect_topic(query)
        all_topics = topic_detector.detect_multiple_topics(query)
        scores = topic_detector.get_topic_similarity_scores(query)
        
        print(f"Query: '{query}'")
        print(f"  Primary: {primary_topic}")
        print(f"  All Topics: {all_topics}")
        print(f"  Top Score: {max(scores.values()):.3f}")
    
    # Test 2: Advanced Chunking
    print(f"\n🔧 Test 2: Advanced Content Processing")
    print("-" * 40)
    
    # Test with a sample file if available
    sample_files = list(Path(cli.vault_path).rglob("*.md"))[:3]
    
    if sample_files:
        for file_path in sample_files[:2]:  # Test first 2 files
            print(f"Processing: {file_path.name}")
            chunks = content_processor.process_file(str(file_path))
            
            print(f"  Generated {len(chunks)} chunks")
            for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
                print(f"    Chunk {i+1}: {chunk['heading']} ({chunk['word_count']} words)")
    else:
        print("  No markdown files found for testing")
    
    # Test 3: Smart Filtering
    print(f"\n🔍 Test 3: Smart Document Filtering")
    print("-" * 40)
    
    # Test topic filtering
    tech_docs = smart_filter.filter_by_topic(cli.documents, "technology")
    philosophy_docs = smart_filter.filter_by_topic(cli.documents, "philosophy")
    performance_docs = smart_filter.filter_by_topic(cli.documents, "performance")
    
    print(f"Technology documents: {len(tech_docs)}")
    print(f"Philosophy documents: {len(philosophy_docs)}")
    print(f"Performance documents: {len(performance_docs)}")
    
    # Test quality filtering
    quality_docs = smart_filter.filter_by_content_quality(cli.documents, min_quality_score=0.5)
    print(f"High quality documents: {len(quality_docs)}")
    
    # Test 4: Re-Ranking
    print(f"\n🔄 Test 4: Re-Ranking")
    print("-" * 25)
    
    # Create sample candidates for testing
    sample_candidates = [
        {
            "content": "Machine learning algorithms are transforming data analysis and pattern recognition in modern applications.",
            "similarity": 0.8,
            "heading": "ML Algorithms"
        },
        {
            "content": "Data analysis techniques include statistical methods, visualization, and machine learning approaches for insights.",
            "similarity": 0.7,
            "heading": "Data Analysis"
        },
        {
            "content": "Philosophical logic deals with reasoning and argumentation in philosophical contexts and formal systems.",
            "similarity": 0.6,
            "heading": "Philosophical Logic"
        }
    ]
    
    test_query = "machine learning algorithms for data analysis"
    reranked = reranker.rerank(test_query, sample_candidates.copy(), top_k=3)
    
    print(f"Query: '{test_query}'")
    print("Re-ranked results:")
    for i, result in enumerate(reranked, 1):
        print(f"  {i}. Final: {result['final_score']:.3f} | "
              f"Original: {result['similarity']:.3f} | "
              f"Rerank: {result['rerank_score']:.3f}")
    
    # Test 5: Enhanced Search
    print(f"\n🚀 Test 5: Enhanced Search with Analysis")
    print("-" * 45)
    
    search_queries = [
        "philosophical currents of logic and mathematics",
        "machine learning algorithms and neural networks",
        "performance optimization techniques"
    ]
    
    all_tests_passed = True
    
    for query in search_queries:
        print(f"\nTesting: '{query}'")
        
        # Search with analysis
        result = await cli.search_with_analysis(query, top_k=3)
        analysis = result['analysis']
        
        print(f"  Results: {analysis['result_count']}")
        print(f"  Primary Topic: {analysis['primary_topic']}")
        print(f"  Quality Score: {analysis['quality_score']:.3f}")
        print(f"  Search Time: {analysis['search_time']:.3f}s")
        
        # Validate quality
        quality_validation = analysis['quality_validation']
        print(f"  Quality Status: {quality_validation['status'].upper()}")
        
        # Check if test passed
        if quality_validation['status'] not in ['excellent', 'good']:
            all_tests_passed = False
        
        # Show top result
        if result['results']:
            top_result = result['results'][0]
            print(f"  Top Result: {top_result.get('final_score', 0):.3f} - {top_result['content'][:60]}...")
    
    # Test 6: System Performance
    print(f"\n⚡ Test 6: System Performance")
    print("-" * 35)
    
    # Test search performance
    start_time = time.time()
    performance_results = []
    
    for query in search_queries:
        result = await cli.search(query, top_k=5)
        performance_results.append(len(result))
    
    total_time = time.time() - start_time
    avg_time = total_time / len(search_queries)
    
    print(f"Total search time: {total_time:.3f}s")
    print(f"Average search time: {avg_time:.3f}s")
    print(f"Results per query: {performance_results}")
    
    # Test 7: Quality Validation
    print(f"\n✅ Test 7: Quality Validation")
    print("-" * 35)
    
    # Test with known good queries
    validation_queries = [
        "philosophical currents of logic and mathematics",
        "performance optimization techniques",
        "machine learning algorithms"
    ]
    
    validation_results = []
    for query in validation_queries:
        results = await cli.search(query, top_k=5)
        validation = quality_validator.validate_search_quality(query, results)
        validation_results.append(validation)
        
        print(f"Query: '{query}'")
        print(f"  Status: {validation['status'].upper()}")
        print(f"  Overall Score: {validation['overall_quality_score']:.3f}")
        print(f"  Similarity Range: {'✅' if validation['similarity_range_valid'] else '❌'}")
        print(f"  Topic Classification: {'✅' if validation['topic_classification_valid'] else '❌'}")
        print(f"  Keyword Relevance: {'✅' if validation['keyword_relevance_valid'] else '❌'}")
    
    # Final Summary
    print(f"\n🎯 Phase 2 Test Summary")
    print("=" * 30)
    
    passed_tests = sum(1 for v in validation_results if v['status'] in ['excellent', 'good'])
    total_tests = len(validation_results)
    
    print(f"Quality Tests Passed: {passed_tests}/{total_tests}")
    print(f"Overall Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"System Performance: {'✅ Good' if avg_time < 2.0 else '⚠️ Needs Optimization'}")
    print(f"All Tests Passed: {'✅ YES' if all_tests_passed else '❌ NO'}")
    
    # Export test results
    test_report = {
        "timestamp": time.time(),
        "total_documents": len(cli.documents),
        "validation_results": validation_results,
        "performance_metrics": {
            "avg_search_time": avg_time,
            "total_search_time": total_time
        },
        "system_stats": cli.get_system_stats()
    }
    
    report_file = "phase2_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(test_report, f, indent=2)
    
    print(f"\n📄 Test report exported to: {report_file}")
    
    return all_tests_passed

if __name__ == "__main__":
    asyncio.run(test_phase2_improvements())
