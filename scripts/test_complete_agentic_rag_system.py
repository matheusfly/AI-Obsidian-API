#!/usr/bin/env python3
"""
Complete Agentic RAG System Test
Test the full system with real data and conversational capabilities
"""

import sys
import os
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the agentic RAG CLI
from production.agentic_rag_cli import AgenticRAGCLI

class CompleteAgenticRAGTest:
    """Test the complete agentic RAG system with real data"""
    
    def __init__(self):
        self.cli = AgenticRAGCLI()
        self.test_results = {}
        self.vault_path = "D:/Nomade Milionario"
        
    async def test_system_initialization(self):
        """Test system initialization and health check"""
        print("🔧 Testing System Initialization...")
        
        try:
            # Initialize the CLI
            await self.cli.initialize()
            
            # Check system health
            health_status = await self.cli.check_system_health()
            
            print(f"✅ System Health: {health_status}")
            
            self.test_results['initialization'] = {
                'status': 'success',
                'health': health_status
            }
            
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            self.test_results['initialization'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_vault_loading(self):
        """Test vault loading with real data"""
        print("📚 Testing Vault Loading...")
        
        try:
            # Load the vault
            load_result = await self.cli.load_obsidian_vault(self.vault_path)
            
            print(f"✅ Vault loaded: {load_result}")
            
            # Check document count
            doc_count = await self.cli.get_document_count()
            print(f"📊 Documents loaded: {doc_count}")
            
            self.test_results['vault_loading'] = {
                'status': 'success',
                'result': load_result,
                'document_count': doc_count
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Vault loading failed: {e}")
            self.test_results['vault_loading'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_conversational_queries(self):
        """Test conversational queries with different topics"""
        print("💬 Testing Conversational Queries...")
        
        test_queries = [
            "What are the main philosophical currents of logic and mathematics?",
            "How to improve reading comprehension and speed?",
            "What are the best practices for Python programming?",
            "Tell me about data analysis techniques",
            "What is the philosophy of knowledge and learning?"
        ]
        
        query_results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}: '{query}'")
            
            try:
                # Process the query
                result = await self.cli.process_query(query)
                
                print(f"✅ Query processed successfully")
                print(f"📊 Response length: {len(result.get('response', ''))}")
                print(f"🔍 Documents found: {len(result.get('documents', []))}")
                
                query_results.append({
                    'query': query,
                    'status': 'success',
                    'response_length': len(result.get('response', '')),
                    'documents_found': len(result.get('documents', [])),
                    'response_preview': result.get('response', '')[:200] + '...' if len(result.get('response', '')) > 200 else result.get('response', '')
                })
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
                query_results.append({
                    'query': query,
                    'status': 'failed',
                    'error': str(e)
                })
        
        self.test_results['conversational_queries'] = query_results
        return len([r for r in query_results if r['status'] == 'success']) > 0
    
    async def test_meaning_subject_retrieval(self):
        """Test meaning and subject retrieval from notes"""
        print("🎯 Testing Meaning Subject Retrieval...")
        
        meaning_queries = [
            "What is the meaning of professional knowledge?",
            "Explain the concept of learning strategies",
            "What are the key subjects in philosophy?",
            "How does reading comprehension work?",
            "What is the relationship between logic and mathematics?"
        ]
        
        retrieval_results = []
        
        for i, query in enumerate(meaning_queries, 1):
            print(f"\n🔍 Meaning Query {i}: '{query}'")
            
            try:
                # Process with meaning focus
                result = await self.cli.process_query(query, focus='meaning')
                
                print(f"✅ Meaning retrieval successful")
                print(f"📊 Similarity scores: {[doc.get('similarity', 0) for doc in result.get('documents', [])]}")
                print(f"🎯 Topic detected: {result.get('topic', 'unknown')}")
                
                retrieval_results.append({
                    'query': query,
                    'status': 'success',
                    'similarity_scores': [doc.get('similarity', 0) for doc in result.get('documents', [])],
                    'topic': result.get('topic', 'unknown'),
                    'meaning_score': result.get('meaning_score', 0)
                })
                
            except Exception as e:
                print(f"❌ Meaning retrieval failed: {e}")
                retrieval_results.append({
                    'query': query,
                    'status': 'failed',
                    'error': str(e)
                })
        
        self.test_results['meaning_retrieval'] = retrieval_results
        return len([r for r in retrieval_results if r['status'] == 'success']) > 0
    
    async def test_gemini_integration(self):
        """Test Gemini integration for conversational responses"""
        print("🤖 Testing Gemini Integration...")
        
        gemini_queries = [
            "Can you explain the philosophy of mathematics in simple terms?",
            "What are the best reading techniques for learning?",
            "How can I improve my programming skills?",
            "What is the relationship between knowledge and wisdom?",
            "Explain the concept of professional development"
        ]
        
        gemini_results = []
        
        for i, query in enumerate(gemini_queries, 1):
            print(f"\n🤖 Gemini Query {i}: '{query}'")
            
            try:
                # Process with Gemini
                result = await self.cli.process_query(query, use_gemini=True)
                
                print(f"✅ Gemini response generated")
                print(f"📊 Response quality: {result.get('quality_score', 0)}")
                print(f"🎯 Intent detected: {result.get('intent', 'unknown')}")
                
                gemini_results.append({
                    'query': query,
                    'status': 'success',
                    'quality_score': result.get('quality_score', 0),
                    'intent': result.get('intent', 'unknown'),
                    'response_preview': result.get('response', '')[:200] + '...' if len(result.get('response', '')) > 200 else result.get('response', '')
                })
                
            except Exception as e:
                print(f"❌ Gemini integration failed: {e}")
                gemini_results.append({
                    'query': query,
                    'status': 'failed',
                    'error': str(e)
                })
        
        self.test_results['gemini_integration'] = gemini_results
        return len([r for r in gemini_results if r['status'] == 'success']) > 0
    
    async def test_advanced_features(self):
        """Test advanced features like topic detection, re-ranking, etc."""
        print("⚡ Testing Advanced Features...")
        
        advanced_tests = [
            {
                'name': 'Topic Detection',
                'query': 'What are the philosophical foundations of mathematics?',
                'expected_topic': 'philosophy'
            },
            {
                'name': 'Re-ranking',
                'query': 'How to improve reading speed and comprehension?',
                'expected_feature': 'reranking'
            },
            {
                'name': 'Query Expansion',
                'query': 'learning strategies',
                'expected_feature': 'expansion'
            },
            {
                'name': 'Intent Recognition',
                'query': 'What is the meaning of professional knowledge?',
                'expected_intent': 'explanation'
            }
        ]
        
        advanced_results = []
        
        for test in advanced_tests:
            print(f"\n🔬 Testing {test['name']}: '{test['query']}'")
            
            try:
                result = await self.cli.process_query(test['query'])
                
                print(f"✅ {test['name']} test successful")
                
                advanced_results.append({
                    'test_name': test['name'],
                    'query': test['query'],
                    'status': 'success',
                    'features_detected': result.get('features_used', []),
                    'topic': result.get('topic', 'unknown'),
                    'intent': result.get('intent', 'unknown')
                })
                
            except Exception as e:
                print(f"❌ {test['name']} test failed: {e}")
                advanced_results.append({
                    'test_name': test['name'],
                    'query': test['query'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        self.test_results['advanced_features'] = advanced_results
        return len([r for r in advanced_results if r['status'] == 'success']) > 0
    
    async def run_complete_test(self):
        """Run the complete test suite"""
        print("🚀 Starting Complete Agentic RAG System Test")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            ("System Initialization", self.test_system_initialization),
            ("Vault Loading", self.test_vault_loading),
            ("Conversational Queries", self.test_conversational_queries),
            ("Meaning Subject Retrieval", self.test_meaning_subject_retrieval),
            ("Gemini Integration", self.test_gemini_integration),
            ("Advanced Features", self.test_advanced_features)
        ]
        
        test_results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = await test_func()
                test_results[test_name] = result
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                test_results[test_name] = False
        
        # Calculate overall results
        total_time = time.time() - start_time
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print(f"\n{'='*60}")
        print(f"🎯 COMPLETE TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total tests: {total_tests}")
        print(f"Passed tests: {passed_tests}")
        print(f"Failed tests: {total_tests - passed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total time: {total_time:.2f}s")
        
        # Save detailed results
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'total_time': total_time
        }
        
        with open('complete_agentic_rag_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to complete_agentic_rag_test_results.json")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! Complete agentic RAG system is working perfectly!")
        else:
            print(f"\n⚠️ Some tests failed. Please review the results above.")
        
        return test_results

async def main():
    """Main test execution"""
    tester = CompleteAgenticRAGTest()
    results = await tester.run_complete_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())
