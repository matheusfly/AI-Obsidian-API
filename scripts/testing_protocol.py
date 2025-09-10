#!/usr/bin/env python3
"""
Revised CLI Testing Protocol
Specific query categories and validation procedures
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from final_comprehensive_rag_cli import FinalComprehensiveRAGCLI

class TestingProtocol:
    """Comprehensive testing protocol for RAG CLI validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cli = None
        self.test_results = []
        
    async def run_complete_testing_protocol(self):
        """Run the complete testing protocol"""
        print("🧪 REVISED CLI TESTING PROTOCOL")
        print("=" * 60)
        print("Following comprehensive testing procedures...")
        print()
        
        try:
            # Initialize CLI
            print("1️⃣ Initializing RAG CLI...")
            self.cli = FinalComprehensiveRAGCLI()
            print("✅ CLI initialized successfully")
            print()
            
            # Run diagnostic tests first
            await self.run_diagnostic_tests()
            
            # Test specific query categories
            await self.test_philosophy_math_queries()
            await self.test_technical_queries()
            await self.test_learning_queries()
            await self.test_business_queries()
            await self.test_general_queries()
            
            # Evaluate response quality
            await self.evaluate_response_quality()
            
            # Track metrics
            await self.track_metrics()
            
            # Generate final report
            self.generate_final_report()
            
        except Exception as e:
            self.logger.error(f"Error in testing protocol: {e}")
            print(f"❌ Testing protocol failed: {e}")
    
    async def run_diagnostic_tests(self):
        """Run diagnostic tests first"""
        print("2️⃣ Running Diagnostic Tests...")
        
        try:
            # Import and run diagnostic tests
            from diagnostic_tests import DiagnosticTester
            tester = DiagnosticTester()
            tester.cli = self.cli
            await tester.run_all_diagnostics()
            
            print("✅ Diagnostic tests completed")
            
        except Exception as e:
            self.logger.warning(f"Error running diagnostic tests: {e}")
            print(f"⚠️ Diagnostic tests had issues: {e}")
    
    async def test_philosophy_math_queries(self):
        """Test Philosophy/Math query category"""
        print("3️⃣ Testing Philosophy/Math Queries...")
        
        test_cases = [
            {
                'query': 'Quais são as principais correntes filosóficas da lógica e matemática?',
                'expected_files': ['LOGICA-INDICE', 'philosophy', 'mathematics'],
                'min_similarity': 0.6,
                'description': 'Philosophy and mathematics query'
            },
            {
                'query': 'What is Platonism in mathematics?',
                'expected_files': ['platonism', 'mathematics', 'philosophy'],
                'min_similarity': 0.6,
                'description': 'Platonism in mathematics'
            },
            {
                'query': 'Explain formalism in mathematical philosophy',
                'expected_files': ['formalism', 'mathematics', 'philosophy'],
                'min_similarity': 0.6,
                'description': 'Mathematical formalism'
            }
        ]
        
        await self._test_query_category('Philosophy/Math', test_cases)
    
    async def test_technical_queries(self):
        """Test Technical query category"""
        print("4️⃣ Testing Technical Queries...")
        
        test_cases = [
            {
                'query': 'Como usar o Scrapy para web scraping?',
                'expected_files': ['scrapy', 'web_scraping', 'python'],
                'min_similarity': 0.6,
                'description': 'Scrapy web scraping'
            },
            {
                'query': 'Machine learning algorithms for data analysis',
                'expected_files': ['machine_learning', 'algorithms', 'data_analysis'],
                'min_similarity': 0.6,
                'description': 'Machine learning algorithms'
            },
            {
                'query': 'Python programming best practices',
                'expected_files': ['python', 'programming', 'best_practices'],
                'min_similarity': 0.6,
                'description': 'Python best practices'
            }
        ]
        
        await self._test_query_category('Technical', test_cases)
    
    async def test_learning_queries(self):
        """Test Learning query category"""
        print("5️⃣ Testing Learning Queries...")
        
        test_cases = [
            {
                'query': 'What is the PQLP reading technique?',
                'expected_files': ['PQLP', 'reading_techniques', 'hyper_reading'],
                'min_similarity': 0.6,
                'description': 'PQLP reading technique'
            },
            {
                'query': 'Speed reading methods and techniques',
                'expected_files': ['speed_reading', 'reading_techniques', 'methods'],
                'min_similarity': 0.6,
                'description': 'Speed reading techniques'
            },
            {
                'query': 'How to improve reading comprehension?',
                'expected_files': ['reading_comprehension', 'learning', 'techniques'],
                'min_similarity': 0.6,
                'description': 'Reading comprehension improvement'
            }
        ]
        
        await self._test_query_category('Learning', test_cases)
    
    async def test_business_queries(self):
        """Test Business query category"""
        print("6️⃣ Testing Business Queries...")
        
        test_cases = [
            {
                'query': 'Business strategy and competitive advantage',
                'expected_files': ['business_strategy', 'competitive_advantage', 'strategy'],
                'min_similarity': 0.6,
                'description': 'Business strategy'
            },
            {
                'query': 'How to conduct market analysis?',
                'expected_files': ['market_analysis', 'business', 'analysis'],
                'min_similarity': 0.6,
                'description': 'Market analysis'
            },
            {
                'query': 'Entrepreneurship and startup strategies',
                'expected_files': ['entrepreneurship', 'startup', 'strategies'],
                'min_similarity': 0.6,
                'description': 'Entrepreneurship strategies'
            }
        ]
        
        await self._test_query_category('Business', test_cases)
    
    async def test_general_queries(self):
        """Test General query category"""
        print("7️⃣ Testing General Queries...")
        
        test_cases = [
            {
                'query': 'What is artificial intelligence?',
                'expected_files': ['artificial_intelligence', 'AI', 'technology'],
                'min_similarity': 0.6,
                'description': 'Artificial intelligence'
            },
            {
                'query': 'How to improve productivity?',
                'expected_files': ['productivity', 'improvement', 'efficiency'],
                'min_similarity': 0.6,
                'description': 'Productivity improvement'
            },
            {
                'query': 'What are the benefits of meditation?',
                'expected_files': ['meditation', 'benefits', 'wellness'],
                'min_similarity': 0.6,
                'description': 'Meditation benefits'
            }
        ]
        
        await self._test_query_category('General', test_cases)
    
    async def _test_query_category(self, category: str, test_cases: List[Dict]):
        """Test a specific query category"""
        category_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"  Testing {i}/{len(test_cases)}: {test_case['description']}")
            
            try:
                # Execute query
                start_time = time.time()
                result = await self.cli.search_command(test_case['query'])
                search_time = time.time() - start_time
                
                # Validate results
                validation = self._validate_query_result(test_case, result)
                
                # Store result
                category_results.append({
                    'query': test_case['query'],
                    'description': test_case['description'],
                    'search_time': search_time,
                    'validation': validation,
                    'result': result
                })
                
                # Print validation results
                if validation['passed']:
                    print(f"    ✅ PASS - {validation['summary']}")
                else:
                    print(f"    ❌ FAIL - {validation['summary']}")
                
            except Exception as e:
                self.logger.error(f"Error testing query: {e}")
                category_results.append({
                    'query': test_case['query'],
                    'description': test_case['description'],
                    'error': str(e),
                    'validation': {'passed': False, 'summary': f'Error: {e}'}
                })
                print(f"    ❌ ERROR - {e}")
        
        # Calculate category success rate
        passed_tests = sum(1 for r in category_results if r.get('validation', {}).get('passed', False))
        success_rate = passed_tests / len(category_results)
        
        print(f"  📊 {category} Success Rate: {success_rate:.1%} ({passed_tests}/{len(category_results)})")
        
        # Store category results
        self.test_results.append({
            'category': category,
            'success_rate': success_rate,
            'passed_tests': passed_tests,
            'total_tests': len(category_results),
            'results': category_results
        })
    
    def _validate_query_result(self, test_case: Dict, result: Dict) -> Dict[str, Any]:
        """Validate a query result"""
        validation = {
            'passed': True,
            'summary': '',
            'details': {}
        }
        
        try:
            # Check if result has required fields
            if 'error' in result:
                validation['passed'] = False
                validation['summary'] = f"Query failed with error: {result['error']}"
                return validation
            
            # Check if results exist
            if 'results' not in result or not result['results']:
                validation['passed'] = False
                validation['summary'] = "No results returned"
                return validation
            
            # Check similarity scores
            similarities = [r.get('similarity', 0) for r in result['results']]
            max_similarity = max(similarities) if similarities else 0
            
            if max_similarity < test_case['min_similarity']:
                validation['passed'] = False
                validation['summary'] = f"Similarity too low: {max_similarity:.3f} < {test_case['min_similarity']}"
                validation['details']['similarity_issue'] = True
            
            # Check if expected files are found
            expected_files = test_case['expected_files']
            found_files = []
            for res in result['results']:
                filename = res.get('filename', '').lower()
                for expected in expected_files:
                    if expected.lower() in filename:
                        found_files.append(expected)
            
            if not found_files:
                validation['details']['no_expected_files'] = True
                # Don't fail for this, just note it
            
            # Check response quality
            if 'response' in result and result['response']:
                response_length = len(result['response'])
                if response_length < 50:
                    validation['details']['short_response'] = True
                elif response_length > 1000:
                    validation['details']['long_response'] = True
            
            # Check quality metrics
            if 'quality_metrics' in result:
                quality_score = result['quality_metrics'].get('overall_score', 0)
                if quality_score < 0.5:
                    validation['details']['low_quality'] = True
            
            # Generate summary
            if validation['passed']:
                validation['summary'] = f"Query successful, {len(result['results'])} results, max similarity: {max_similarity:.3f}"
            else:
                validation['summary'] = f"Query failed validation"
            
            return validation
            
        except Exception as e:
            validation['passed'] = False
            validation['summary'] = f"Validation error: {e}"
            return validation
    
    async def evaluate_response_quality(self):
        """Evaluate response quality across all queries"""
        print("8️⃣ Evaluating Response Quality...")
        
        try:
            quality_metrics = {
                'total_queries': 0,
                'high_quality_responses': 0,
                'medium_quality_responses': 0,
                'low_quality_responses': 0,
                'average_quality_score': 0,
                'average_search_time': 0,
                'average_results_count': 0
            }
            
            all_quality_scores = []
            all_search_times = []
            all_results_counts = []
            
            for category_result in self.test_results:
                for query_result in category_result['results']:
                    if 'result' in query_result and 'quality_metrics' in query_result['result']:
                        quality_metrics['total_queries'] += 1
                        
                        quality_score = query_result['result']['quality_metrics'].get('overall_score', 0)
                        all_quality_scores.append(quality_score)
                        
                        search_time = query_result.get('search_time', 0)
                        all_search_times.append(search_time)
                        
                        results_count = len(query_result['result'].get('results', []))
                        all_results_counts.append(results_count)
                        
                        # Categorize quality
                        if quality_score >= 0.8:
                            quality_metrics['high_quality_responses'] += 1
                        elif quality_score >= 0.6:
                            quality_metrics['medium_quality_responses'] += 1
                        else:
                            quality_metrics['low_quality_responses'] += 1
            
            # Calculate averages
            if all_quality_scores:
                quality_metrics['average_quality_score'] = sum(all_quality_scores) / len(all_quality_scores)
            if all_search_times:
                quality_metrics['average_search_time'] = sum(all_search_times) / len(all_search_times)
            if all_results_counts:
                quality_metrics['average_results_count'] = sum(all_results_counts) / len(all_results_counts)
            
            # Print quality evaluation
            print(f"  📊 Quality Evaluation Results:")
            print(f"    Total Queries: {quality_metrics['total_queries']}")
            print(f"    High Quality (≥0.8): {quality_metrics['high_quality_responses']}")
            print(f"    Medium Quality (0.6-0.8): {quality_metrics['medium_quality_responses']}")
            print(f"    Low Quality (<0.6): {quality_metrics['low_quality_responses']}")
            print(f"    Average Quality Score: {quality_metrics['average_quality_score']:.3f}")
            print(f"    Average Search Time: {quality_metrics['average_search_time']:.2f}s")
            print(f"    Average Results Count: {quality_metrics['average_results_count']:.1f}")
            
            # Store quality metrics
            self.quality_metrics = quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating response quality: {e}")
            print(f"❌ Error evaluating response quality: {e}")
    
    async def track_metrics(self):
        """Track comprehensive metrics"""
        print("9️⃣ Tracking Comprehensive Metrics...")
        
        try:
            # Calculate overall metrics
            total_categories = len(self.test_results)
            total_queries = sum(cat['total_tests'] for cat in self.test_results)
            total_passed = sum(cat['passed_tests'] for cat in self.test_results)
            
            overall_success_rate = total_passed / total_queries if total_queries > 0 else 0
            
            # Category success rates
            category_success_rates = {
                cat['category']: cat['success_rate'] for cat in self.test_results
            }
            
            # Performance metrics
            performance_metrics = {
                'overall_success_rate': overall_success_rate,
                'total_categories': total_categories,
                'total_queries': total_queries,
                'total_passed': total_passed,
                'category_success_rates': category_success_rates
            }
            
            # Print metrics
            print(f"  📈 Comprehensive Metrics:")
            print(f"    Overall Success Rate: {overall_success_rate:.1%}")
            print(f"    Total Categories: {total_categories}")
            print(f"    Total Queries: {total_queries}")
            print(f"    Total Passed: {total_passed}")
            print(f"    Category Success Rates:")
            for category, rate in category_success_rates.items():
                print(f"      {category}: {rate:.1%}")
            
            # Store metrics
            self.performance_metrics = performance_metrics
            
        except Exception as e:
            self.logger.error(f"Error tracking metrics: {e}")
            print(f"❌ Error tracking metrics: {e}")
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n📊 FINAL TESTING REPORT")
        print("=" * 60)
        
        try:
            # Calculate overall statistics
            total_categories = len(self.test_results)
            total_queries = sum(cat['total_tests'] for cat in self.test_results)
            total_passed = sum(cat['passed_tests'] for cat in self.test_results)
            overall_success_rate = total_passed / total_queries if total_queries > 0 else 0
            
            print(f"Overall Success Rate: {overall_success_rate:.1%}")
            print(f"Total Categories: {total_categories}")
            print(f"Total Queries: {total_queries}")
            print(f"Total Passed: {total_passed}")
            print()
            
            # Category breakdown
            print("Category Breakdown:")
            print("-" * 30)
            for category_result in self.test_results:
                category = category_result['category']
                success_rate = category_result['success_rate']
                passed = category_result['passed_tests']
                total = category_result['total_tests']
                
                status_icon = "✅" if success_rate >= 0.8 else "⚠️" if success_rate >= 0.6 else "❌"
                print(f"{status_icon} {category}: {success_rate:.1%} ({passed}/{total})")
            
            print()
            
            # Quality metrics
            if hasattr(self, 'quality_metrics'):
                print("Quality Metrics:")
                print("-" * 20)
                print(f"Average Quality Score: {self.quality_metrics['average_quality_score']:.3f}")
                print(f"Average Search Time: {self.quality_metrics['average_search_time']:.2f}s")
                print(f"Average Results Count: {self.quality_metrics['average_results_count']:.1f}")
                print()
            
            # Overall assessment
            if overall_success_rate >= 0.9:
                print("🎉 EXCELLENT! System is production-ready.")
            elif overall_success_rate >= 0.8:
                print("✅ GOOD! System is ready with minor improvements.")
            elif overall_success_rate >= 0.6:
                print("⚠️ FAIR! System needs improvements before production.")
            else:
                print("❌ POOR! System needs significant improvements.")
            
            # Save detailed report
            report_data = {
                'timestamp': time.time(),
                'overall_success_rate': overall_success_rate,
                'total_categories': total_categories,
                'total_queries': total_queries,
                'total_passed': total_passed,
                'category_results': self.test_results,
                'quality_metrics': getattr(self, 'quality_metrics', {}),
                'performance_metrics': getattr(self, 'performance_metrics', {})
            }
            
            report_file = Path("testing_protocol_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"\n📁 Detailed report saved to: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating final report: {e}")
            print(f"❌ Error generating final report: {e}")

# Main execution
async def main():
    """Main function to run testing protocol"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run testing protocol
    protocol = TestingProtocol()
    await protocol.run_complete_testing_protocol()

if __name__ == "__main__":
    asyncio.run(main())
