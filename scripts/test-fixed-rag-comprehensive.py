#!/usr/bin/env python3
"""
Comprehensive test for the fixed RAG system
"""

import asyncio
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from fixed_agentic_rag_cli import FixedAgenticRAGCLI
from rag_quality_validator import RAGQualityValidator

async def test_fixed_rag_comprehensive():
    """Comprehensive test of the fixed RAG system"""
    print("🧪 Testing Fixed RAG System - Comprehensive Test")
    print("=" * 60)
    
    # Initialize CLI and validator
    cli = FixedAgenticRAGCLI()
    validator = RAGQualityValidator()
    
    # Test queries with expected outcomes
    test_cases = [
        {
            "query": "philosophical currents of logic and mathematics",
            "expected_topics": ["logic_mathematics"],
            "expected_keywords": ["logic", "mathematics", "philosophy", "reasoning"]
        },
        {
            "query": "performance optimization techniques",
            "expected_topics": ["performance"],
            "expected_keywords": ["performance", "optimization", "speed", "efficiency"]
        },
        {
            "query": "machine learning algorithms",
            "expected_topics": ["machine_learning"],
            "expected_keywords": ["machine learning", "algorithms", "neural", "ai"]
        }
    ]
    
    all_tests_passed = True
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: '{test_case['query']}'")
        print("-" * 40)
        
        # Run search
        results = await cli.search(test_case['query'], top_k=5)
        
        # Display results
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            score = result.get('final_score', result.get('similarity', 0))
            topic = result.get('metadata', {}).get('topic', 'unknown')
            content_preview = result['content'][:100].replace('\n', ' ')
            print(f"  {i}. Score: {score:.3f} | Topic: {topic} | {content_preview}...")
        
        # Validate quality
        validation = validator.validate_search_quality(test_case['query'], results)
        
        print(f"\n📊 Quality Analysis:")
        print(f"   Overall Score: {validation['overall_quality_score']:.2f}")
        print(f"   Status: {validation['status'].upper()}")
        print(f"   Similarity Range: {'✅ PASS' if validation['similarity_range_valid'] else '❌ FAIL'}")
        print(f"   Topic Classification: {'✅ PASS' if validation['topic_classification_valid'] else '❌ FAIL'}")
        print(f"   Keyword Relevance: {'✅ PASS' if validation['keyword_relevance_valid'] else '❌ FAIL'}")
        
        # Check for critical issues
        if 'critical_issue' in validation:
            print(f"   🚨 CRITICAL ISSUE: {validation['critical_issue']['message']}")
            all_tests_passed = False
        
        if validation['status'] not in ['excellent', 'good']:
            all_tests_passed = False
    
    # Final summary
    print(f"\n🎯 Final Test Result: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    
    # Export validation report
    report_file = validator.export_validation_report()
    print(f"📄 Validation report exported to: {report_file}")
    
    return all_tests_passed

if __name__ == "__main__":
    asyncio.run(test_fixed_rag_comprehensive())
