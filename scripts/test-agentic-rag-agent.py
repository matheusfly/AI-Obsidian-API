#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agentic RAG Agent
Tests Phase 3 agent capabilities including prompt engineering and memory
"""

import asyncio
import sys
import time
from pathlib import Path
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from agentic_rag_agent import AgenticRAGAgent

async def test_agentic_rag_agent():
    """Comprehensive test of the agentic RAG agent"""
    print("🤖 Agentic RAG Agent - Comprehensive Test")
    print("=" * 60)
    
    # Initialize agent
    agent = AgenticRAGAgent()
    
    # Test 1: Basic Agent Capabilities
    print("\n🧠 Test 1: Basic Agent Capabilities")
    print("-" * 40)
    
    test_queries = [
        "philosophical currents of logic and mathematics",
        "machine learning algorithms and neural networks",
        "performance optimization techniques",
        "business strategy and management"
    ]
    
    for query in test_queries:
        print(f"\nTesting: '{query}'")
        
        # Process query
        result = await agent.process_query(query)
        
        print(f"  Response Length: {len(result['response'])} chars")
        print(f"  Confidence: {result['agent_metrics']['confidence']:.3f}")
        print(f"  Response Time: {result['agent_metrics']['response_time']:.3f}s")
        print(f"  Sources Used: {result['agent_metrics']['sources_used']}")
        print(f"  Topic: {result['agent_metrics']['topic']}")
        print(f"  Complexity: {result['agent_metrics']['complexity']}")
        
        # Show follow-up suggestions
        if result['follow_up_suggestions']:
            print(f"  Follow-ups: {len(result['follow_up_suggestions'])} suggestions")
    
    # Test 2: Conversation Memory
    print(f"\n💭 Test 2: Conversation Memory")
    print("-" * 35)
    
    # Simulate conversation
    conversation_queries = [
        "What is machine learning?",
        "How does it relate to neural networks?",
        "Can you give me examples of ML algorithms?",
        "What about performance optimization in ML?"
    ]
    
    for i, query in enumerate(conversation_queries, 1):
        print(f"\nConversation Turn {i}: '{query}'")
        
        result = await agent.process_query(query, user_id="test_user")
        
        # Check conversation context
        context = result['conversation_context']
        print(f"  Context Length: {len(context)} previous turns")
        print(f"  Response: {result['response'][:100]}...")
        
        # Check if agent maintains context
        if i > 1:
            print(f"  Context Maintained: {'✅' if len(context) > 0 else '❌'}")
    
    # Test 3: Prompt Engineering
    print(f"\n📝 Test 3: Prompt Engineering")
    print("-" * 35)
    
    # Test different prompt templates
    prompt_tests = [
        ("philosophy", "What is logical reasoning?"),
        ("technology", "How do neural networks work?"),
        ("performance", "What are optimization techniques?"),
        ("business", "What is strategic planning?")
    ]
    
    for topic, query in prompt_tests:
        print(f"\nTesting {topic} prompt: '{query}'")
        
        result = await agent.process_query(query)
        
        # Check if appropriate prompt was used
        detected_topic = result['agent_metrics']['topic']
        print(f"  Detected Topic: {detected_topic}")
        print(f"  Prompt Match: {'✅' if topic == detected_topic else '❌'}")
        print(f"  Response Quality: {result['agent_metrics']['confidence']:.3f}")
    
    # Test 4: User Preferences
    print(f"\n👤 Test 4: User Preferences")
    print("-" * 35)
    
    # Test with different users
    users = ["user1", "user2", "user3"]
    
    for user_id in users:
        print(f"\nTesting user: {user_id}")
        
        # Simulate user interactions
        user_queries = [
            "machine learning algorithms",
            "neural network architecture",
            "deep learning applications"
        ]
        
        for query in user_queries:
            result = await agent.process_query(query, user_id=user_id)
        
        # Check user preferences
        user_prefs = agent.user_preferences.get(user_id, {})
        print(f"  Preferred Topics: {len(user_prefs.get('preferred_topics', set()))}")
        print(f"  Query Patterns: {len(user_prefs.get('query_patterns', []))}")
    
    # Test 5: Agent Status and Metrics
    print(f"\n📊 Test 5: Agent Status and Metrics")
    print("-" * 40)
    
    status = agent.get_agent_status()
    
    print(f"Conversation Length: {status['conversation_length']}")
    print(f"Queries Processed: {status['session_metrics']['queries_processed']}")
    print(f"Average Response Time: {status['session_metrics']['avg_response_time']:.3f}s")
    print(f"Topics Discussed: {len(status['session_metrics']['topics_discussed'])}")
    print(f"User Preferences Count: {status['user_preferences_count']}")
    
    # Test 6: Error Handling
    print(f"\n⚠️ Test 6: Error Handling")
    print("-" * 30)
    
    # Test with empty query
    result = await agent.process_query("")
    print(f"Empty Query Handling: {'✅' if 'error' in result else '❌'}")
    
    # Test with very long query
    long_query = "What is " + "machine learning " * 100
    result = await agent.process_query(long_query)
    print(f"Long Query Handling: {'✅' if not result.get('error') else '❌'}")
    
    # Test 7: Performance Metrics
    print(f"\n⚡ Test 7: Performance Metrics")
    print("-" * 35)
    
    # Test response time consistency
    response_times = []
    for i in range(5):
        start_time = time.time()
        result = await agent.process_query(f"test query {i}")
        response_time = time.time() - start_time
        response_times.append(response_time)
    
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)
    min_response_time = min(response_times)
    
    print(f"Average Response Time: {avg_response_time:.3f}s")
    print(f"Max Response Time: {max_response_time:.3f}s")
    print(f"Min Response Time: {min_response_time:.3f}s")
    print(f"Performance Consistency: {'✅' if max_response_time < 5.0 else '❌'}")
    
    # Test 8: Memory Management
    print(f"\n🧠 Test 8: Memory Management")
    print("-" * 35)
    
    # Test conversation history limits
    initial_length = len(agent.conversation_history)
    
    # Add many queries to test memory limits
    for i in range(60):  # More than maxlen=50
        await agent.process_query(f"memory test query {i}")
    
    final_length = len(agent.conversation_history)
    
    print(f"Initial History Length: {initial_length}")
    print(f"Final History Length: {final_length}")
    print(f"Memory Limit Respected: {'✅' if final_length <= 50 else '❌'}")
    
    # Final Summary
    print(f"\n🎯 Test Summary")
    print("=" * 30)
    
    # Calculate test results
    total_tests = 8
    passed_tests = 0
    
    # Check basic functionality
    if status['session_metrics']['queries_processed'] > 0:
        passed_tests += 1
    
    # Check conversation memory
    if status['conversation_length'] > 0:
        passed_tests += 1
    
    # Check user preferences
    if status['user_preferences_count'] > 0:
        passed_tests += 1
    
    # Check performance
    if status['session_metrics']['avg_response_time'] < 5.0:
        passed_tests += 1
    
    # Check memory management
    if final_length <= 50:
        passed_tests += 1
    
    # Check error handling
    if not result.get('error'):
        passed_tests += 1
    
    # Check confidence scores
    if result['agent_metrics']['confidence'] > 0.0:
        passed_tests += 1
    
    # Check follow-up suggestions
    if len(result['follow_up_suggestions']) > 0:
        passed_tests += 1
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Overall Status: {'✅ PASS' if passed_tests >= 6 else '❌ FAIL'}")
    
    # Export test results
    test_report = {
        "timestamp": time.time(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "agent_status": status,
        "performance_metrics": {
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time
        }
    }
    
    report_file = "agentic_rag_agent_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(test_report, f, indent=2)
    
    print(f"\n📄 Test report exported to: {report_file}")
    
    return passed_tests >= 6

if __name__ == "__main__":
    asyncio.run(test_agentic_rag_agent())
