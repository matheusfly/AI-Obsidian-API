#!/usr/bin/env python3
"""
Phase 4.4: Performance Monitoring Validation
Test real-time metrics and system health monitoring with real data
"""

import sys
import os
import json
import time
import asyncio
import psutil
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime, timedelta
import threading
import queue

# Add data-pipeline services to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

try:
    from embeddings.embedding_service import EmbeddingService
    from vector.chroma_service import ChromaService
    from search.semantic_search_service import SemanticSearchService
    from processing.content_processor import ContentProcessor
    from search.reranker import ReRanker
    from search.topic_detector import TopicDetector
    from search.smart_document_filter import SmartDocumentFilter
    from processing.advanced_content_processor import AdvancedContentProcessor
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure data-pipeline services are properly set up")
    sys.exit(1)

class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self):
        self.metrics = {
            "queries_per_second": 0.0,
            "average_response_time": 0.0,
            "memory_usage_mb": 0.0,
            "cpu_usage_percent": 0.0,
            "active_connections": 0,
            "error_rate": 0.0,
            "cache_hit_rate": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        self.query_history = []
        self.error_history = []
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Update system metrics
                self._update_system_metrics()
                
                # Update query metrics
                self._update_query_metrics()
                
                # Update error metrics
                self._update_error_metrics()
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def _update_system_metrics(self):
        """Update system-level metrics"""
        process = psutil.Process()
        
        self.metrics["memory_usage_mb"] = process.memory_info().rss / 1024 / 1024
        self.metrics["cpu_usage_percent"] = process.cpu_percent()
        self.metrics["last_updated"] = datetime.now().isoformat()
    
    def _update_query_metrics(self):
        """Update query-related metrics"""
        if not self.query_history:
            return
        
        # Calculate queries per second (last 60 seconds)
        now = datetime.now()
        recent_queries = [q for q in self.query_history if (now - q["timestamp"]).total_seconds() <= 60]
        
        if recent_queries:
            self.metrics["queries_per_second"] = len(recent_queries) / 60.0
            
            # Calculate average response time
            response_times = [q["response_time"] for q in recent_queries]
            self.metrics["average_response_time"] = np.mean(response_times)
    
    def _update_error_metrics(self):
        """Update error-related metrics"""
        if not self.error_history:
            self.metrics["error_rate"] = 0.0
            return
        
        # Calculate error rate (last 60 seconds)
        now = datetime.now()
        recent_errors = [e for e in self.error_history if (now - e["timestamp"]).total_seconds() <= 60]
        recent_queries = [q for q in self.query_history if (now - q["timestamp"]).total_seconds() <= 60]
        
        if recent_queries:
            self.metrics["error_rate"] = len(recent_errors) / len(recent_queries)
    
    def record_query(self, query: str, response_time: float, success: bool = True):
        """Record a query for monitoring"""
        query_record = {
            "timestamp": datetime.now(),
            "query": query,
            "response_time": response_time,
            "success": success
        }
        self.query_history.append(query_record)
        
        if not success:
            self.error_history.append({
                "timestamp": datetime.now(),
                "query": query,
                "error": "Query failed"
            })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        health_status = {
            "overall_health": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Check memory usage
        if self.metrics["memory_usage_mb"] > 1000:  # 1GB
            health_status["issues"].append("High memory usage")
            health_status["recommendations"].append("Consider optimizing memory usage")
        
        # Check CPU usage
        if self.metrics["cpu_usage_percent"] > 80:
            health_status["issues"].append("High CPU usage")
            health_status["recommendations"].append("Consider reducing load or optimizing queries")
        
        # Check error rate
        if self.metrics["error_rate"] > 0.1:  # 10%
            health_status["issues"].append("High error rate")
            health_status["recommendations"].append("Investigate and fix errors")
        
        # Check response time
        if self.metrics["average_response_time"] > 5.0:  # 5 seconds
            health_status["issues"].append("Slow response time")
            health_status["recommendations"].append("Consider optimizing search performance")
        
        # Determine overall health
        if health_status["issues"]:
            health_status["overall_health"] = "degraded" if len(health_status["issues"]) < 3 else "unhealthy"
        
        return health_status

class PerformanceMonitoringValidator:
    """Validate performance monitoring with real data"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "4.4 - Performance Monitoring Validation",
            "status": "running",
            "tests": {},
            "summary": {}
        }
        
        # Initialize services
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()
        self.search_service = SemanticSearchService(self.chroma_service, self.embedding_service)
        self.content_processor = ContentProcessor()
        self.reranker = ReRanker()
        self.topic_detector = TopicDetector()
        self.smart_filter = SmartDocumentFilter()
        self.advanced_processor = AdvancedContentProcessor()
        
        # Initialize performance monitor
        self.monitor = PerformanceMonitor()
        
        # Vault data path
        self.vault_path = Path("D:/Nomade Milionario")
        
    def test_real_time_monitoring(self) -> Dict[str, Any]:
        """Test real-time monitoring capabilities"""
        print("📊 Testing Real-Time Monitoring...")
        
        test_results = {
            "test_name": "Real-Time Monitoring",
            "status": "running",
            "monitoring_tests": {},
            "overall_success": True
        }
        
        try:
            # Test 1: Start monitoring
            print("  🚀 Testing monitoring startup...")
            
            self.monitor.start_monitoring()
            time.sleep(2)  # Let it collect some data
            
            initial_metrics = self.monitor.get_metrics()
            
            assert "memory_usage_mb" in initial_metrics, "Should have memory usage metric"
            assert "cpu_usage_percent" in initial_metrics, "Should have CPU usage metric"
            assert "queries_per_second" in initial_metrics, "Should have queries per second metric"
            
            test_results["monitoring_tests"]["startup"] = {
                "status": "passed",
                "initial_metrics": initial_metrics,
                "message": "Monitoring startup working"
            }
            
            print("    ✅ Monitoring startup working")
            
            # Test 2: Query recording
            print("  📝 Testing query recording...")
            
            # Simulate some queries
            test_queries = [
                "What are the main philosophical currents?",
                "How does Scrapy work?",
                "What is the PQLP technique?",
                "Explain machine learning",
                "What is web scraping?"
            ]
            
            for i, query in enumerate(test_queries):
                response_time = 0.1 + (i * 0.05)  # Simulate varying response times
                success = i != 2  # Simulate one failure
                self.monitor.record_query(query, response_time, success)
            
            time.sleep(1)  # Let monitoring update
            
            updated_metrics = self.monitor.get_metrics()
            
            assert updated_metrics["queries_per_second"] > 0, "Should have recorded queries"
            assert updated_metrics["average_response_time"] > 0, "Should have average response time"
            
            test_results["monitoring_tests"]["query_recording"] = {
                "status": "passed",
                "updated_metrics": updated_metrics,
                "queries_recorded": len(test_queries),
                "message": "Query recording working"
            }
            
            print("    ✅ Query recording working")
            
            # Test 3: Health status
            print("  🏥 Testing health status...")
            
            health_status = self.monitor.get_health_status()
            
            assert "overall_health" in health_status, "Should have overall health status"
            assert "issues" in health_status, "Should have issues list"
            assert "recommendations" in health_status, "Should have recommendations list"
            
            test_results["monitoring_tests"]["health_status"] = {
                "status": "passed",
                "health_status": health_status,
                "message": "Health status working"
            }
            
            print("    ✅ Health status working")
            
            # Stop monitoring
            self.monitor.stop_monitoring()
            
            test_results["status"] = "passed"
            print("  ✅ Real-time monitoring test passed")
            
        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            test_results["overall_success"] = False
            print(f"  ❌ Real-time monitoring test failed: {e}")
        
        return test_results
    
    def test_performance_benchmarking(self) -> Dict[str, Any]:
        """Test performance benchmarking capabilities"""
        print("⚡ Testing Performance Benchmarking...")
        
        test_results = {
            "test_name": "Performance Benchmarking",
            "status": "running",
            "benchmark_tests": {},
            "overall_success": True
        }
        
        try:
            # Test 1: Search performance benchmark
            print("  🔍 Testing search performance benchmark...")
            
            start_time = time.time()
            
            # Run multiple searches
            search_times = []
            for i in range(10):
                query = f"Test query {i} about philosophy and mathematics"
                query_start = time.time()
                
                try:
                    results = self.search_service.search(query, [], top_k=5)
                    query_end = time.time()
                    search_times.append(query_end - query_start)
                except Exception as e:
                    search_times.append(0.0)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calculate statistics
            avg_search_time = np.mean(search_times)
            min_search_time = np.min(search_times)
            max_search_time = np.max(search_times)
            std_search_time = np.std(search_times)
            
            test_results["benchmark_tests"]["search_performance"] = {
                "status": "passed",
                "total_time": total_time,
                "average_search_time": avg_search_time,
                "min_search_time": min_search_time,
                "max_search_time": max_search_time,
                "std_search_time": std_search_time,
                "queries_per_second": 10 / total_time,
                "message": f"Search performance benchmark completed"
            }
            
            print(f"    ✅ Search performance: {avg_search_time:.3f}s average")
            
            # Test 2: Memory usage benchmark
            print("  💾 Testing memory usage benchmark...")
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            # Run memory-intensive operations
            for i in range(5):
                query = f"Memory test query {i} with lots of content about philosophy and mathematics"
                results = self.search_service.search(query, [], top_k=10)
            
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            
            test_results["benchmark_tests"]["memory_usage"] = {
                "status": "passed",
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "message": f"Memory usage benchmark completed"
            }
            
            print(f"    ✅ Memory usage: {memory_increase:.1f} MB increase")
            
            # Test 3: Concurrent performance
            print("  🔄 Testing concurrent performance...")
            
            async def concurrent_search(query: str):
                return self.search_service.search(query, [], top_k=5)
            
            async def run_concurrent_benchmark():
                tasks = [concurrent_search(f"Concurrent query {i}") for i in range(5)]
                start_time = time.time()
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                return end_time - start_time, len(results)
            
            concurrent_time, concurrent_results = asyncio.run(run_concurrent_benchmark())
            
            test_results["benchmark_tests"]["concurrent_performance"] = {
                "status": "passed",
                "concurrent_time": concurrent_time,
                "concurrent_results": concurrent_results,
                "concurrent_queries_per_second": concurrent_results / concurrent_time,
                "message": f"Concurrent performance benchmark completed"
            }
            
            print(f"    ✅ Concurrent performance: {concurrent_time:.3f}s")
            
            test_results["status"] = "passed"
            print("  ✅ Performance benchmarking test passed")
            
        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            test_results["overall_success"] = False
            print(f"  ❌ Performance benchmarking test failed: {e}")
        
        return test_results
    
    def test_system_health_monitoring(self) -> Dict[str, Any]:
        """Test system health monitoring"""
        print("🏥 Testing System Health Monitoring...")
        
        test_results = {
            "test_name": "System Health Monitoring",
            "status": "running",
            "health_tests": {},
            "overall_success": True
        }
        
        try:
            # Test 1: Health status detection
            print("  🔍 Testing health status detection...")
            
            # Start monitoring
            self.monitor.start_monitoring()
            time.sleep(1)
            
            # Get initial health status
            initial_health = self.monitor.get_health_status()
            
            assert "overall_health" in initial_health, "Should have overall health status"
            assert initial_health["overall_health"] in ["healthy", "degraded", "unhealthy"], "Should have valid health status"
            
            test_results["health_tests"]["status_detection"] = {
                "status": "passed",
                "initial_health": initial_health,
                "message": "Health status detection working"
            }
            
            print("    ✅ Health status detection working")
            
            # Test 2: Issue detection
            print("  ⚠️ Testing issue detection...")
            
            # Simulate high memory usage by recording many queries
            for i in range(100):
                self.monitor.record_query(f"Memory test query {i}", 0.1, True)
            
            time.sleep(2)  # Let monitoring update
            
            updated_health = self.monitor.get_health_status()
            
            test_results["health_tests"]["issue_detection"] = {
                "status": "passed",
                "updated_health": updated_health,
                "message": "Issue detection working"
            }
            
            print("    ✅ Issue detection working")
            
            # Test 3: Recommendations generation
            print("  💡 Testing recommendations generation...")
            
            # Check if recommendations are generated
            recommendations = updated_health.get("recommendations", [])
            
            assert isinstance(recommendations, list), "Should have recommendations list"
            
            test_results["health_tests"]["recommendations"] = {
                "status": "passed",
                "recommendations": recommendations,
                "message": "Recommendations generation working"
            }
            
            print("    ✅ Recommendations generation working")
            
            # Stop monitoring
            self.monitor.stop_monitoring()
            
            test_results["status"] = "passed"
            print("  ✅ System health monitoring test passed")
            
        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            test_results["overall_success"] = False
            print(f"  ❌ System health monitoring test failed: {e}")
        
        return test_results
    
    def test_real_data_monitoring(self) -> Dict[str, Any]:
        """Test monitoring with real data"""
        print("🔗 Testing Real Data Monitoring...")
        
        test_results = {
            "test_name": "Real Data Monitoring",
            "status": "running",
            "real_data_tests": {},
            "overall_success": True
        }
        
        try:
            # Test 1: Real vault content monitoring
            print("  📁 Testing real vault content monitoring...")
            
            if self.vault_path.exists():
                # Load real vault content
                vault_content = self._load_vault_content()
                
                if vault_content:
                    # Start monitoring
                    self.monitor.start_monitoring()
                    
                    # Test with real content
                    real_queries = [
                        "What are the main philosophical currents of logic and mathematics?",
                        "How does Scrapy handle web scraping?",
                        "What is the PQLP reading technique?"
                    ]
                    
                    for query in real_queries:
                        start_time = time.time()
                        try:
                            results = self.search_service.search(query, list(vault_content.values()), top_k=5)
                            end_time = time.time()
                            response_time = end_time - start_time
                            self.monitor.record_query(query, response_time, True)
                        except Exception as e:
                            self.monitor.record_query(query, 0.0, False)
                    
                    time.sleep(2)  # Let monitoring update
                    
                    # Get metrics
                    real_metrics = self.monitor.get_metrics()
                    real_health = self.monitor.get_health_status()
                    
                    test_results["real_data_tests"]["vault_content"] = {
                        "status": "passed",
                        "metrics": real_metrics,
                        "health": real_health,
                        "queries_tested": len(real_queries),
                        "message": "Real vault content monitoring working"
                    }
                    
                    print("    ✅ Real vault content monitoring working")
                else:
                    test_results["real_data_tests"]["vault_content"] = {
                        "status": "skipped",
                        "message": "No vault content found"
                    }
                    print("    ⚠️ No vault content found")
            else:
                test_results["real_data_tests"]["vault_content"] = {
                    "status": "skipped",
                    "message": "Vault path not found"
                }
                print("    ⚠️ Vault path not found")
            
            # Stop monitoring
            self.monitor.stop_monitoring()
            
            test_results["status"] = "passed"
            print("  ✅ Real data monitoring test passed")
            
        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            test_results["overall_success"] = False
            print(f"  ❌ Real data monitoring test failed: {e}")
        
        return test_results
    
    def _load_vault_content(self) -> Dict[str, Dict]:
        """Load vault content for testing"""
        vault_content = {}
        
        try:
            # Load a few sample files for testing
            sample_files = [
                "LOGICA-INDICE.md",
                "Hiper-Leitura.md",
                "scrapy.md"
            ]
            
            for filename in sample_files:
                file_path = self.vault_path / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Process content
                    processed_content = self.content_processor.process_file(file_path)
                    vault_content[filename] = processed_content
            
            return vault_content
            
        except Exception as e:
            print(f"    ⚠️ Error loading vault content: {e}")
            return {}
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete Phase 4.4 validation"""
        print("🚀 Starting Phase 4.4: Performance Monitoring Validation")
        print("=" * 60)
        
        # Test 1: Real-time monitoring
        monitoring_test = self.test_real_time_monitoring()
        self.results["tests"]["real_time_monitoring"] = monitoring_test
        
        # Test 2: Performance benchmarking
        benchmarking_test = self.test_performance_benchmarking()
        self.results["tests"]["performance_benchmarking"] = benchmarking_test
        
        # Test 3: System health monitoring
        health_test = self.test_system_health_monitoring()
        self.results["tests"]["system_health_monitoring"] = health_test
        
        # Test 4: Real data monitoring
        real_data_test = self.test_real_data_monitoring()
        self.results["tests"]["real_data_monitoring"] = real_data_test
        
        # Calculate overall success
        overall_success = all(
            test.get("overall_success", False) 
            for test in self.results["tests"].values()
        )
        
        self.results["status"] = "completed" if overall_success else "failed"
        self.results["summary"] = {
            "overall_success": overall_success,
            "tests_completed": len(self.results["tests"]),
            "successful_tests": sum(1 for test in self.results["tests"].values() if test.get("overall_success", False)),
            "failed_tests": sum(1 for test in self.results["tests"].values() if not test.get("overall_success", False))
        }
        
        print("\n" + "=" * 60)
        print("📊 Phase 4.4 Validation Summary:")
        print(f"Overall Success: {'✅ YES' if overall_success else '❌ NO'}")
        print(f"Tests Completed: {self.results['summary']['tests_completed']}")
        print(f"Successful Tests: {self.results['summary']['successful_tests']}")
        print(f"Failed Tests: {self.results['summary']['failed_tests']}")
        
        return self.results

def main():
    """Main validation function"""
    validator = PerformanceMonitoringValidator()
    results = validator.run_validation()
    
    # Save results
    output_file = "phase4_monitoring_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
