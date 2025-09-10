#!/usr/bin/env python3
"""
Comprehensive Test Suite for Quality System
Tests Phase 4 quality evaluation and feedback collection
"""

import asyncio
import sys
import time
from pathlib import Path
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from quality_evaluator import QualityEvaluator
from quality_agentic_rag_cli import QualityAgenticRAGCLI

async def test_quality_system():
    """Comprehensive test of the quality system"""
    print("🧪 Quality System - Comprehensive Test")
    print("=" * 60)
    
    # Test 1: Quality Evaluator
    print("\n📊 Test 1: Quality Evaluator")
    print("-" * 40)
    
    evaluator = QualityEvaluator()
    
    # Test cases with different quality levels
    test_cases = [
        {
            "query": "What are machine learning algorithms?",
            "response": "Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed. They include supervised learning, unsupervised learning, and reinforcement learning approaches.",
            "retrieved_docs": [
                {
                    "content": "Machine learning algorithms are powerful tools for data analysis and pattern recognition.",
                    "similarity": 0.8
                },
                {
                    "content": "Supervised learning uses labeled data to train models for prediction tasks.",
                    "similarity": 0.7
                }
            ],
            "expected_quality": "good"
        },
        {
            "query": "How does neural network training work?",
            "response": "Neural network training involves forward propagation, backpropagation, and gradient descent optimization to minimize loss functions.",
            "retrieved_docs": [
                {
                    "content": "Neural networks are trained using backpropagation and gradient descent algorithms.",
                    "similarity": 0.9
                }
            ],
            "expected_quality": "excellent"
        },
        {
            "query": "What is the philosophy of logic?",
            "response": "I don't know about that topic.",
            "retrieved_docs": [],
            "expected_quality": "poor"
        },
        {
            "query": "Performance optimization techniques",
            "response": "Performance optimization includes caching, indexing, algorithm improvements, and resource management strategies.",
            "retrieved_docs": [
                {
                    "content": "Performance optimization techniques can improve system efficiency and reduce response times.",
                    "similarity": 0.6
                },
                {
                    "content": "Caching strategies help reduce database load and improve response times.",
                    "similarity": 0.5
                }
            ],
            "expected_quality": "good"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['query']}")
        
        # Evaluate quality
        evaluation = evaluator.evaluate_response(
            test_case['query'],
            test_case['response'],
            test_case['retrieved_docs']
        )
        
        print(f"  Overall Score: {evaluation['overall_score']:.3f}")
        print(f"  Quality Level: {evaluation['quality_level']}")
        print(f"  Expected: {test_case['expected_quality']}")
        print(f"  Match: {'✅' if evaluation['quality_level'] == test_case['expected_quality'] else '❌'}")
        
        # Show detailed metrics
        metrics = evaluation['metrics']
        print(f"  Basic Metrics:")
        print(f"    Keyword Coverage: {metrics['basic']['keyword_coverage']:.3f}")
        print(f"    Length Score: {metrics['basic']['length_score']:.3f}")
        print(f"  Semantic Metrics:")
        print(f"    Semantic Similarity: {metrics['semantic']['semantic_similarity']:.3f}")
        print(f"    Doc Alignment: {metrics['semantic']['doc_alignment']:.3f}")
        print(f"  Relevance Metrics:")
        print(f"    Query Coverage: {metrics['relevance']['query_coverage']:.3f}")
        print(f"    Source Utilization: {metrics['relevance']['source_utilization']:.3f}")
        
        if evaluation['recommendations']:
            print(f"  Recommendations: {len(evaluation['recommendations'])}")
    
    # Test 2: User Feedback Collection
    print(f"\n📝 Test 2: User Feedback Collection")
    print("-" * 45)
    
    feedback_test_cases = [
        ("What are machine learning algorithms?", "Machine learning algorithms are...", "positive", "Very helpful!"),
        ("How does neural network training work?", "Neural network training involves...", "negative", "Too technical"),
        ("What is the philosophy of logic?", "I don't know about that topic.", "negative", "No information provided"),
        ("Performance optimization techniques", "Performance optimization includes...", "neutral", "")
    ]
    
    for query, response, feedback_type, notes in feedback_test_cases:
        feedback = evaluator.collect_user_feedback(query, response, feedback_type, notes)
        print(f"  {feedback_type.upper()}: {query[:30]}... -> {feedback['timestamp']}")
    
    # Test 3: Quality Analytics
    print(f"\n📈 Test 3: Quality Analytics")
    print("-" * 35)
    
    # Generate quality report
    report = evaluator.get_quality_report()
    
    print(f"Total Evaluations: {report['total_evaluations']}")
    print(f"Average Quality Score: {report['avg_quality_score']:.3f}")
    print(f"Quality Distribution: {report['quality_distribution']}")
    print(f"Feedback Distribution: {report['feedback_distribution']}")
    
    if report['recommendations']:
        print(f"System Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    # Test 4: Quality-Enhanced CLI
    print(f"\n🤖 Test 4: Quality-Enhanced CLI")
    print("-" * 40)
    
    cli = QualityAgenticRAGCLI()
    
    # Test query processing
    test_queries = [
        "What are machine learning algorithms?",
        "How does neural network training work?",
        "What is the philosophy of logic?",
        "Performance optimization techniques"
    ]
    
    for query in test_queries:
        print(f"\nTesting: '{query}'")
        
        # Process query
        result = await cli.process_query_with_quality(query)
        
        print(f"  Response Length: {len(result['response'])} chars")
        print(f"  Processing Time: {result['processing_time']:.3f}s")
        
        if result.get('quality_evaluation'):
            quality = result['quality_evaluation']
            print(f"  Quality Score: {quality['overall_score']:.3f}")
            print(f"  Quality Level: {quality['quality_level']}")
            print(f"  Recommendations: {len(quality['recommendations'])}")
        
        # Simulate feedback
        feedback_type = 'positive' if result.get('quality_evaluation', {}).get('overall_score', 0) > 0.6 else 'negative'
        cli.quality_evaluator.collect_user_feedback(query, result['response'], feedback_type)
    
    # Test 5: System Status
    print(f"\n📊 Test 5: System Status")
    print("-" * 30)
    
    status = cli.get_system_status()
    
    print(f"Agent Status:")
    print(f"  Conversations: {status['agent_status']['conversation_length']}")
    print(f"  Queries Processed: {status['agent_status']['session_metrics']['queries_processed']}")
    print(f"  Avg Response Time: {status['agent_status']['session_metrics']['avg_response_time']:.3f}s")
    
    print(f"Quality Metrics:")
    print(f"  Total Evaluations: {status['quality_metrics']['total_evaluations']}")
    print(f"  Average Score: {status['quality_metrics']['avg_quality_score']:.3f}")
    print(f"  Feedback Collected: {status['total_feedback_collected']}")
    
    # Test 6: Data Export
    print(f"\n💾 Test 6: Data Export")
    print("-" * 25)
    
    export_file = cli.export_quality_data("test_quality_data.json")
    print(f"Quality data exported to: {export_file}")
    
    # Verify export file
    if Path(export_file).exists():
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        print(f"Exported data contains:")
        print(f"  Quality History: {len(exported_data['quality_history'])} items")
        print(f"  User Feedback: {len(exported_data['user_feedback_history'])} items")
        print(f"  Quality Analytics: {len(exported_data['quality_analytics'])} metrics")
        print("  Export Status: ✅ SUCCESS")
    else:
        print("  Export Status: ❌ FAILED")
    
    # Test 7: Performance Testing
    print(f"\n⚡ Test 7: Performance Testing")
    print("-" * 35)
    
    # Test evaluation performance
    evaluation_times = []
    for i in range(10):
        start_time = time.time()
        evaluation = evaluator.evaluate_response(
            "Test query for performance",
            "Test response for performance testing",
            [{"content": "Test document", "similarity": 0.5}]
        )
        evaluation_time = time.time() - start_time
        evaluation_times.append(evaluation_time)
    
    avg_evaluation_time = sum(evaluation_times) / len(evaluation_times)
    max_evaluation_time = max(evaluation_times)
    min_evaluation_time = min(evaluation_times)
    
    print(f"Evaluation Performance:")
    print(f"  Average Time: {avg_evaluation_time:.3f}s")
    print(f"  Max Time: {max_evaluation_time:.3f}s")
    print(f"  Min Time: {min_evaluation_time:.3f}s")
    print(f"  Performance: {'✅ GOOD' if avg_evaluation_time < 1.0 else '❌ SLOW'}")
    
    # Test 8: Error Handling
    print(f"\n⚠️ Test 8: Error Handling")
    print("-" * 30)
    
    # Test with empty inputs
    empty_evaluation = evaluator.evaluate_response("", "", [])
    print(f"Empty Inputs: {'✅' if empty_evaluation['overall_score'] == 0.0 else '❌'}")
    
    # Test with None inputs
    try:
        none_evaluation = evaluator.evaluate_response(None, None, None)
        print(f"None Inputs: {'✅' if none_evaluation else '❌'}")
    except Exception as e:
        print(f"None Inputs: ❌ Error: {e}")
    
    # Test with malformed documents
    malformed_docs = [{"content": "test", "similarity": "invalid"}]
    try:
        malformed_evaluation = evaluator.evaluate_response("test", "test", malformed_docs)
        print(f"Malformed Docs: ✅ Handled gracefully")
    except Exception as e:
        print(f"Malformed Docs: ❌ Error: {e}")
    
    # Final Summary
    print(f"\n🎯 Test Summary")
    print("=" * 30)
    
    # Calculate test results
    total_tests = 8
    passed_tests = 0
    
    # Check quality evaluator
    if report['total_evaluations'] > 0:
        passed_tests += 1
    
    # Check feedback collection
    if len(evaluator.user_feedback) > 0:
        passed_tests += 1
    
    # Check CLI functionality
    if status['total_queries_processed'] > 0:
        passed_tests += 1
    
    # Check data export
    if Path(export_file).exists():
        passed_tests += 1
    
    # Check performance
    if avg_evaluation_time < 2.0:
        passed_tests += 1
    
    # Check error handling
    if empty_evaluation['overall_score'] == 0.0:
        passed_tests += 1
    
    # Check quality metrics
    if status['quality_metrics']['avg_quality_score'] > 0.0:
        passed_tests += 1
    
    # Check system integration
    if status['total_feedback_collected'] > 0:
        passed_tests += 1
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Overall Status: {'✅ PASS' if passed_tests >= 6 else '❌ FAIL'}")
    
    return passed_tests >= 6

if __name__ == "__main__":
    asyncio.run(test_quality_system())
