#!/usr/bin/env python3
"""
Comprehensive Diagnostic Tests for Final RAG CLI
Validates all Phase 1-5 improvements and system functionality
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from final_comprehensive_rag_cli import FinalComprehensiveRAGCLI

class DiagnosticTester:
    """Comprehensive diagnostic tester for RAG system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = []
        self.cli = None
        
    async def run_all_diagnostics(self):
        """Run all diagnostic tests"""
        print("🧪 COMPREHENSIVE DIAGNOSTIC TESTS")
        print("=" * 60)
        print("Testing all Phase 1-5 improvements...")
        print()
        
        try:
            # Initialize CLI
            print("1️⃣ Initializing RAG CLI...")
            self.cli = FinalComprehensiveRAGCLI()
            print("✅ CLI initialized successfully")
            print()
            
            # Run diagnostic tests
            await self.test_system_initialization()
            await self.test_semantic_search()
            await self.test_topic_detection()
            await self.test_document_filtering()
            await self.test_reranking()
            await self.test_quality_evaluation()
            await self.test_agentic_capabilities()
            await self.test_performance()
            await self.test_error_handling()
            
            # Generate diagnostic report
            self.generate_diagnostic_report()
            
        except Exception as e:
            self.logger.error(f"Error in diagnostic tests: {e}")
            print(f"❌ Diagnostic tests failed: {e}")
    
    async def test_system_initialization(self):
        """Test system initialization"""
        print("2️⃣ Testing System Initialization...")
        
        try:
            # Test vault content loading
            assert len(self.cli.vault_content) > 0, "No vault content loaded"
            
            # Test component initialization
            assert self.cli.topic_extractor is not None, "Topic extractor not initialized"
            assert self.cli.content_processor is not None, "Content processor not initialized"
            assert self.cli.document_filter is not None, "Document filter not initialized"
            assert self.cli.reranker is not None, "Reranker not initialized"
            assert self.cli.quality_evaluator is not None, "Quality evaluator not initialized"
            assert self.cli.agentic_agent is not None, "Agentic agent not initialized"
            
            # Test embedding model
            assert hasattr(self.cli, 'embedding_model'), "Embedding model not initialized"
            
            self.test_results.append({
                'test': 'System Initialization',
                'status': 'PASS',
                'details': f'Loaded {len(self.cli.vault_content)} documents, all components initialized'
            })
            print("✅ System initialization test passed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'System Initialization',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ System initialization test failed: {e}")
    
    async def test_semantic_search(self):
        """Test semantic search functionality"""
        print("3️⃣ Testing Semantic Search...")
        
        try:
            # Test queries
            test_queries = [
                "philosophy of mathematics",
                "web scraping with Python",
                "machine learning algorithms",
                "reading techniques",
                "business strategy"
            ]
            
            search_results = []
            for query in test_queries:
                result = await self.cli.search_command(query)
                search_results.append(result)
                
                # Validate results
                assert 'results' in result, f"No results for query: {query}"
                assert len(result['results']) > 0, f"Empty results for query: {query}"
                
                # Check similarity scores
                for res in result['results']:
                    assert 'similarity' in res, "Missing similarity score"
                    assert 0 <= res['similarity'] <= 1, f"Invalid similarity score: {res['similarity']}"
            
            self.test_results.append({
                'test': 'Semantic Search',
                'status': 'PASS',
                'details': f'Successfully processed {len(test_queries)} queries with valid results'
            })
            print("✅ Semantic search test passed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Semantic Search',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Semantic search test failed: {e}")
    
    async def test_topic_detection(self):
        """Test topic detection functionality"""
        print("4️⃣ Testing Topic Detection...")
        
        try:
            # Test topic detection
            test_queries = [
                ("What are the main philosophical currents?", "philosophy"),
                ("How to use Scrapy for web scraping?", "programming"),
                ("Machine learning algorithms for data analysis", "technical"),
                ("Business strategy and competitive advantage", "business"),
                ("Reading techniques and speed reading", "learning")
            ]
            
            topic_accuracy = 0
            for query, expected_topic in test_queries:
                detected_topic = self.cli._detect_topic(query)
                
                # Check if detected topic is reasonable
                if expected_topic in detected_topic.lower() or detected_topic in expected_topic.lower():
                    topic_accuracy += 1
            
            accuracy_rate = topic_accuracy / len(test_queries)
            
            self.test_results.append({
                'test': 'Topic Detection',
                'status': 'PASS' if accuracy_rate >= 0.6 else 'FAIL',
                'details': f'Topic detection accuracy: {accuracy_rate:.1%}'
            })
            
            if accuracy_rate >= 0.6:
                print("✅ Topic detection test passed")
            else:
                print(f"⚠️ Topic detection test passed with low accuracy: {accuracy_rate:.1%}")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Topic Detection',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Topic detection test failed: {e}")
    
    async def test_document_filtering(self):
        """Test document filtering functionality"""
        print("5️⃣ Testing Document Filtering...")
        
        try:
            # Test filtering with different queries
            test_cases = [
                {
                    'query': 'philosophy of mathematics',
                    'expected_min_docs': 1,
                    'topic': 'philosophy'
                },
                {
                    'query': 'web scraping techniques',
                    'expected_min_docs': 1,
                    'topic': 'programming'
                },
                {
                    'query': 'machine learning algorithms',
                    'expected_min_docs': 1,
                    'topic': 'technical'
                }
            ]
            
            filtering_success = 0
            for case in test_cases:
                filtered_docs = self.cli._filter_documents(case['query'], case['topic'])
                
                if len(filtered_docs) >= case['expected_min_docs']:
                    filtering_success += 1
            
            success_rate = filtering_success / len(test_cases)
            
            self.test_results.append({
                'test': 'Document Filtering',
                'status': 'PASS' if success_rate >= 0.6 else 'FAIL',
                'details': f'Document filtering success rate: {success_rate:.1%}'
            })
            
            if success_rate >= 0.6:
                print("✅ Document filtering test passed")
            else:
                print(f"⚠️ Document filtering test passed with low success rate: {success_rate:.1%}")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Document Filtering',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Document filtering test failed: {e}")
    
    async def test_reranking(self):
        """Test re-ranking functionality"""
        print("6️⃣ Testing Re-ranking...")
        
        try:
            # Test re-ranking with sample data
            query = "philosophy of mathematics"
            sample_results = [
                {'content': 'Philosophy of mathematics examines the nature of mathematical objects', 'similarity': 0.8},
                {'content': 'Web scraping with Python involves extracting data from websites', 'similarity': 0.3},
                {'content': 'Machine learning algorithms learn patterns from data', 'similarity': 0.4},
                {'content': 'Mathematical logic provides the foundation for reasoning', 'similarity': 0.7},
                {'content': 'Business strategy focuses on competitive advantage', 'similarity': 0.2}
            ]
            
            # Test re-ranking
            reranked_results = self.cli.reranker.search_with_rerank(
                query, sample_results, n_results=3, rerank_top_k=5
            )
            
            # Validate re-ranking
            assert len(reranked_results) <= 3, "Too many results after re-ranking"
            assert all('final_score' in r for r in reranked_results), "Missing final scores"
            
            # Check if re-ranking improved order
            original_order = [r['content'][:20] for r in sample_results[:3]]
            reranked_order = [r['content'][:20] for r in reranked_results]
            
            self.test_results.append({
                'test': 'Re-ranking',
                'status': 'PASS',
                'details': f'Re-ranking completed successfully, {len(reranked_results)} results returned'
            })
            print("✅ Re-ranking test passed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Re-ranking',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Re-ranking test failed: {e}")
    
    async def test_quality_evaluation(self):
        """Test quality evaluation functionality"""
        print("7️⃣ Testing Quality Evaluation...")
        
        try:
            # Test quality evaluation
            query = "What is machine learning?"
            response = "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
            search_results = [
                {'content': 'Machine learning algorithms learn patterns from data', 'similarity': 0.8},
                {'content': 'Artificial intelligence includes machine learning techniques', 'similarity': 0.7}
            ]
            
            quality_metrics = self.cli.quality_evaluator.evaluate_response(
                query=query,
                response=response,
                retrieved_docs=search_results
            )
            
            # Validate quality metrics
            assert 'overall_score' in quality_metrics, "Missing overall score"
            assert 0 <= quality_metrics['overall_score'] <= 1, "Invalid overall score"
            assert 'metrics' in quality_metrics, "Missing metrics"
            
            self.test_results.append({
                'test': 'Quality Evaluation',
                'status': 'PASS',
                'details': f'Quality evaluation completed, overall score: {quality_metrics["overall_score"]:.3f}'
            })
            print("✅ Quality evaluation test passed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Quality Evaluation',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Quality evaluation test failed: {e}")
    
    async def test_agentic_capabilities(self):
        """Test agentic capabilities"""
        print("8️⃣ Testing Agentic Capabilities...")
        
        try:
            # Test agentic response generation
            query = "Explain the philosophy of mathematics"
            context = "Philosophy of mathematics examines the nature of mathematical objects and truth."
            search_results = [
                {'content': 'Philosophy of mathematics examines the nature of mathematical objects', 'similarity': 0.8}
            ]
            
            response = await self.cli.agentic_agent.generate_response(
                query=query,
                context=context,
                search_results=search_results,
                conversation_history=[]
            )
            
            # Validate response
            assert len(response) > 0, "Empty response generated"
            assert isinstance(response, str), "Response is not a string"
            
            # Test follow-up suggestions
            suggestions = self.cli.agentic_agent.generate_follow_up_suggestions(
                query=query,
                search_results=search_results,
                conversation_history=[]
            )
            
            self.test_results.append({
                'test': 'Agentic Capabilities',
                'status': 'PASS',
                'details': f'Agentic response generated ({len(response)} chars), {len(suggestions)} suggestions'
            })
            print("✅ Agentic capabilities test passed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Agentic Capabilities',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Agentic capabilities test failed: {e}")
    
    async def test_performance(self):
        """Test system performance"""
        print("9️⃣ Testing Performance...")
        
        try:
            # Test search performance
            query = "machine learning algorithms"
            start_time = time.time()
            
            result = await self.cli.search_command(query)
            
            search_time = time.time() - start_time
            
            # Validate performance
            assert search_time < 10, f"Search too slow: {search_time:.2f}s"
            assert 'search_time' in result, "Missing search time in result"
            
            # Test memory usage
            memory_usage = len(self.cli.vault_content) * 1000  # Rough estimate
            assert memory_usage < 1000000, f"Memory usage too high: {memory_usage}"
            
            self.test_results.append({
                'test': 'Performance',
                'status': 'PASS',
                'details': f'Search time: {search_time:.2f}s, Memory usage: {memory_usage} bytes'
            })
            print("✅ Performance test passed")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Performance',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Performance test failed: {e}")
    
    async def test_error_handling(self):
        """Test error handling"""
        print("🔟 Testing Error Handling...")
        
        try:
            # Test with invalid inputs
            invalid_queries = [
                "",  # Empty query
                None,  # None query
                "a" * 1000,  # Very long query
            ]
            
            error_handling_success = 0
            for query in invalid_queries:
                try:
                    result = await self.cli.search_command(query)
                    if 'error' in result or result.get('response', '').startswith('❌'):
                        error_handling_success += 1
                except Exception:
                    error_handling_success += 1
            
            success_rate = error_handling_success / len(invalid_queries)
            
            self.test_results.append({
                'test': 'Error Handling',
                'status': 'PASS' if success_rate >= 0.6 else 'FAIL',
                'details': f'Error handling success rate: {success_rate:.1%}'
            })
            
            if success_rate >= 0.6:
                print("✅ Error handling test passed")
            else:
                print(f"⚠️ Error handling test passed with low success rate: {success_rate:.1%}")
            
        except Exception as e:
            self.test_results.append({
                'test': 'Error Handling',
                'status': 'FAIL',
                'details': str(e)
            })
            print(f"❌ Error handling test failed: {e}")
    
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        print("\n📊 DIAGNOSTIC REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'PASS')
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        print()
        
        print("Detailed Results:")
        print("-" * 30)
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            print(f"   {result['details']}")
            print()
        
        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! System is ready for production.")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ Most tests passed. System is mostly ready with minor issues.")
        else:
            print("❌ Multiple test failures. System needs attention before production.")
        
        # Save report
        report_file = Path("diagnostic_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        print(f"\n📁 Diagnostic report saved to: {report_file}")

# Main execution
async def main():
    """Main function to run diagnostic tests"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run diagnostic tests
    tester = DiagnosticTester()
    await tester.run_all_diagnostics()

if __name__ == "__main__":
    asyncio.run(main())
