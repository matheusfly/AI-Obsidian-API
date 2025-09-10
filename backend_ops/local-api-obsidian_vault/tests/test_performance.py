#!/usr/bin/env python3
"""
⚡ PERFORMANCE TESTING SUITE
Comprehensive performance benchmarks for Obsidian Vault AI System
Version: 3.0.0 - Production Ready
"""

import asyncio
import httpx
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any, Optional
import pytest
import pytest_benchmark
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import os

# Test Configuration
BASE_URL = "http://localhost:8080"
OBSIDIAN_API_URL = "http://localhost:27123"
TEST_TIMEOUT = 30.0
CONCURRENT_REQUESTS = 50
STRESS_TEST_DURATION = 300  # 5 minutes

class PerformanceTestSuite:
    """Comprehensive Performance Testing Suite"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.obsidian_url = OBSIDIAN_API_URL
        self.results = {}
        self.start_time = time.time()
        
    async def run_all_benchmarks(self):
        """Run complete performance benchmark suite"""
        print("⚡ STARTING PERFORMANCE BENCHMARK SUITE")
        print("=" * 60)
        
        # Performance Tests
        await self.benchmark_api_response_times()
        await self.benchmark_concurrent_requests()
        await self.benchmark_memory_usage()
        await self.benchmark_search_performance()
        await self.benchmark_ai_operations()
        await self.benchmark_file_operations()
        await self.benchmark_stress_testing()
        await self.benchmark_reliability()
        
        # Generate performance report
        await self.generate_performance_report()
        
        return self.results
    
    async def benchmark_api_response_times(self):
        """Benchmark 1: API Response Times"""
        print("\n1️⃣ Benchmarking API Response Times...")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/metrics", "Metrics"),
            ("/api/v1/notes", "Notes Listing"),
            ("/api/v1/mcp/tools", "MCP Tools"),
            ("/api/v1/performance/metrics", "Performance Metrics")
        ]
        
        response_times = {}
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            for endpoint, description in endpoints:
                times = []
                
                # Run 10 requests for each endpoint
                for _ in range(10):
                    start_time = time.time()
                    try:
                        response = await client.get(f"{self.base_url}{endpoint}")
                        end_time = time.time()
                        
                        if response.status_code == 200:
                            times.append((end_time - start_time) * 1000)  # Convert to ms
                    except Exception as e:
                        print(f"  ⚠️ Error testing {description}: {e}")
                
                if times:
                    response_times[description] = {
                        "avg": statistics.mean(times),
                        "min": min(times),
                        "max": max(times),
                        "p95": self.percentile(times, 95),
                        "p99": self.percentile(times, 99)
                    }
                    
                    print(f"  📊 {description}:")
                    print(f"    Average: {response_times[description]['avg']:.2f}ms")
                    print(f"    Min: {response_times[description]['min']:.2f}ms")
                    print(f"    Max: {response_times[description]['max']:.2f}ms")
                    print(f"    95th percentile: {response_times[description]['p95']:.2f}ms")
        
        self.results["api_response_times"] = response_times
    
    async def benchmark_concurrent_requests(self):
        """Benchmark 2: Concurrent Request Handling"""
        print("\n2️⃣ Benchmarking Concurrent Request Handling...")
        
        concurrent_levels = [1, 5, 10, 25, 50, 100]
        concurrent_results = {}
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            for concurrency in concurrent_levels:
                print(f"  🔄 Testing {concurrency} concurrent requests...")
                
                start_time = time.time()
                tasks = []
                
                # Create concurrent tasks
                for _ in range(concurrency):
                    task = client.get(f"{self.base_url}/health")
                    tasks.append(task)
                
                # Execute all tasks concurrently
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                # Analyze results
                successful = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
                failed = concurrency - successful
                total_time = (end_time - start_time) * 1000
                avg_time = total_time / concurrency
                success_rate = (successful / concurrency) * 100
                
                concurrent_results[concurrency] = {
                    "successful": successful,
                    "failed": failed,
                    "success_rate": success_rate,
                    "total_time": total_time,
                    "avg_time": avg_time,
                    "requests_per_second": concurrency / (total_time / 1000)
                }
                
                print(f"    ✅ Success: {successful}/{concurrency} ({success_rate:.1f}%)")
                print(f"    ⏱️ Total time: {total_time:.2f}ms")
                print(f"    📈 RPS: {concurrent_results[concurrency]['requests_per_second']:.2f}")
        
        self.results["concurrent_requests"] = concurrent_results
    
    async def benchmark_memory_usage(self):
        """Benchmark 3: Memory Usage Analysis"""
        print("\n3️⃣ Benchmarking Memory Usage...")
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_samples = []
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Run various operations and monitor memory
            operations = [
                ("Health Check", lambda: client.get(f"{self.base_url}/health")),
                ("Search", lambda: client.post(f"{self.base_url}/api/v1/search", json={"query": "test", "limit": 10})),
                ("Notes", lambda: client.get(f"{self.base_url}/api/v1/notes")),
                ("Metrics", lambda: client.get(f"{self.base_url}/metrics"))
            ]
            
            for operation_name, operation_func in operations:
                # Run operation multiple times
                for _ in range(10):
                    try:
                        await operation_func()
                        current_memory = process.memory_info().rss / 1024 / 1024
                        memory_samples.append({
                            "operation": operation_name,
                            "memory_mb": current_memory,
                            "timestamp": time.time()
                        })
                    except Exception as e:
                        print(f"  ⚠️ Error in {operation_name}: {e}")
                
                # Small delay between operations
                await asyncio.sleep(0.1)
        
        # Analyze memory usage
        if memory_samples:
            memory_values = [sample["memory_mb"] for sample in memory_samples]
            peak_memory = max(memory_values)
            avg_memory = statistics.mean(memory_values)
            memory_growth = peak_memory - initial_memory
            
            memory_analysis = {
                "initial_memory_mb": initial_memory,
                "peak_memory_mb": peak_memory,
                "avg_memory_mb": avg_memory,
                "memory_growth_mb": memory_growth,
                "samples": len(memory_samples)
            }
            
            print(f"  📊 Memory Analysis:")
            print(f"    Initial: {initial_memory:.2f}MB")
            print(f"    Peak: {peak_memory:.2f}MB")
            print(f"    Average: {avg_memory:.2f}MB")
            print(f"    Growth: {memory_growth:.2f}MB")
            
            self.results["memory_usage"] = memory_analysis
    
    async def benchmark_search_performance(self):
        """Benchmark 4: Search Performance"""
        print("\n4️⃣ Benchmarking Search Performance...")
        
        search_queries = [
            "artificial intelligence",
            "machine learning algorithms",
            "data science methodologies",
            "project management techniques",
            "software architecture patterns",
            "neural networks deep learning",
            "natural language processing",
            "computer vision applications",
            "reinforcement learning",
            "agile development methodology"
        ]
        
        search_results = {}
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test basic search
            print("  🔍 Testing basic search performance...")
            basic_times = []
            
            for query in search_queries:
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/search",
                        json={"query": query, "limit": 10, "semantic": False}
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        basic_times.append((end_time - start_time) * 1000)
                except Exception as e:
                    print(f"    ⚠️ Error with query '{query}': {e}")
            
            if basic_times:
                search_results["basic_search"] = {
                    "avg_time": statistics.mean(basic_times),
                    "min_time": min(basic_times),
                    "max_time": max(basic_times),
                    "p95_time": self.percentile(basic_times, 95)
                }
            
            # Test semantic search
            print("  🧠 Testing semantic search performance...")
            semantic_times = []
            
            for query in search_queries:
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/search",
                        json={"query": query, "limit": 10, "semantic": True}
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        semantic_times.append((end_time - start_time) * 1000)
                except Exception as e:
                    print(f"    ⚠️ Error with semantic query '{query}': {e}")
            
            if semantic_times:
                search_results["semantic_search"] = {
                    "avg_time": statistics.mean(semantic_times),
                    "min_time": min(semantic_times),
                    "max_time": max(semantic_times),
                    "p95_time": self.percentile(semantic_times, 95)
                }
            
            # Test enhanced RAG
            print("  🤖 Testing enhanced RAG performance...")
            rag_times = []
            
            for query in search_queries[:5]:  # Test subset for RAG
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/rag/enhanced",
                        json={
                            "query": query,
                            "agent_id": "performance_test_agent",
                            "use_hierarchical": True,
                            "max_depth": 3
                        }
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        rag_times.append((end_time - start_time) * 1000)
                except Exception as e:
                    print(f"    ⚠️ Error with RAG query '{query}': {e}")
            
            if rag_times:
                search_results["enhanced_rag"] = {
                    "avg_time": statistics.mean(rag_times),
                    "min_time": min(rag_times),
                    "max_time": max(rag_times),
                    "p95_time": self.percentile(rag_times, 95)
                }
        
        self.results["search_performance"] = search_results
        
        # Print summary
        for search_type, metrics in search_results.items():
            print(f"  📊 {search_type.replace('_', ' ').title()}:")
            print(f"    Average: {metrics['avg_time']:.2f}ms")
            print(f"    95th percentile: {metrics['p95_time']:.2f}ms")
    
    async def benchmark_ai_operations(self):
        """Benchmark 5: AI Operations Performance"""
        print("\n5️⃣ Benchmarking AI Operations...")
        
        ai_operations = {}
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test AI retrieval
            print("  🧠 Testing AI retrieval performance...")
            ai_retrieval_times = []
            
            for i in range(10):
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/ai/retrieve",
                        json={
                            "query": f"AI concept {i}",
                            "agent_id": f"perf_agent_{i}",
                            "context": {"search_type": "semantic", "limit": 5}
                        }
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        ai_retrieval_times.append((end_time - start_time) * 1000)
                except Exception as e:
                    print(f"    ⚠️ Error in AI retrieval {i}: {e}")
            
            if ai_retrieval_times:
                ai_operations["ai_retrieval"] = {
                    "avg_time": statistics.mean(ai_retrieval_times),
                    "min_time": min(ai_retrieval_times),
                    "max_time": max(ai_retrieval_times),
                    "p95_time": self.percentile(ai_retrieval_times, 95)
                }
            
            # Test batch processing
            print("  📦 Testing batch processing performance...")
            batch_times = []
            
            for i in range(5):
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/rag/batch",
                        json={
                            "queries": [f"batch query {i}_{j}" for j in range(5)],
                            "agent_id": f"batch_agent_{i}",
                            "batch_size": 3
                        }
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        batch_times.append((end_time - start_time) * 1000)
                except Exception as e:
                    print(f"    ⚠️ Error in batch processing {i}: {e}")
            
            if batch_times:
                ai_operations["batch_processing"] = {
                    "avg_time": statistics.mean(batch_times),
                    "min_time": min(batch_times),
                    "max_time": max(batch_times),
                    "p95_time": self.percentile(batch_times, 95)
                }
        
        self.results["ai_operations"] = ai_operations
        
        # Print summary
        for operation, metrics in ai_operations.items():
            print(f"  📊 {operation.replace('_', ' ').title()}:")
            print(f"    Average: {metrics['avg_time']:.2f}ms")
            print(f"    95th percentile: {metrics['p95_time']:.2f}ms")
    
    async def benchmark_file_operations(self):
        """Benchmark 6: File Operations Performance"""
        print("\n6️⃣ Benchmarking File Operations...")
        
        file_operations = {}
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test file creation
            print("  📝 Testing file creation performance...")
            create_times = []
            
            for i in range(10):
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/notes",
                        json={
                            "path": f"perf-test-{i}.md",
                            "content": f"# Performance Test File {i}\n\nThis is a test file for performance benchmarking.\n\nCreated at: {datetime.now().isoformat()}",
                            "tags": ["performance", "test", f"file-{i}"]
                        }
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        create_times.append((end_time - start_time) * 1000)
                except Exception as e:
                    print(f"    ⚠️ Error creating file {i}: {e}")
            
            if create_times:
                file_operations["file_creation"] = {
                    "avg_time": statistics.mean(create_times),
                    "min_time": min(create_times),
                    "max_time": max(create_times),
                    "p95_time": self.percentile(create_times, 95)
                }
            
            # Test file reading
            print("  📖 Testing file reading performance...")
            read_times = []
            
            for i in range(10):
                start_time = time.time()
                try:
                    response = await client.get(f"{self.base_url}/api/v1/notes/perf-test-{i}.md")
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        read_times.append((end_time - start_time) * 1000)
                except Exception as e:
                    print(f"    ⚠️ Error reading file {i}: {e}")
            
            if read_times:
                file_operations["file_reading"] = {
                    "avg_time": statistics.mean(read_times),
                    "min_time": min(read_times),
                    "max_time": max(read_times),
                    "p95_time": self.percentile(read_times, 95)
                }
        
        self.results["file_operations"] = file_operations
        
        # Print summary
        for operation, metrics in file_operations.items():
            print(f"  📊 {operation.replace('_', ' ').title()}:")
            print(f"    Average: {metrics['avg_time']:.2f}ms")
            print(f"    95th percentile: {metrics['p95_time']:.2f}ms")
    
    async def benchmark_stress_testing(self):
        """Benchmark 7: Stress Testing"""
        print("\n7️⃣ Running Stress Test...")
        
        stress_results = {
            "duration_seconds": 60,  # 1 minute stress test
            "concurrent_requests": 20,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "max_response_time": 0,
            "min_response_time": float('inf'),
            "requests_per_second": 0
        }
        
        start_time = time.time()
        response_times = []
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            while (time.time() - start_time) < stress_results["duration_seconds"]:
                # Create batch of concurrent requests
                tasks = []
                for _ in range(stress_results["concurrent_requests"]):
                    task = client.get(f"{self.base_url}/health")
                    tasks.append(task)
                
                # Execute batch
                batch_start = time.time()
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                batch_end = time.time()
                
                # Analyze batch results
                for response in responses:
                    stress_results["total_requests"] += 1
                    
                    if hasattr(response, 'status_code') and response.status_code == 200:
                        stress_results["successful_requests"] += 1
                        response_times.append((batch_end - batch_start) * 1000)
                    else:
                        stress_results["failed_requests"] += 1
                
                # Small delay between batches
                await asyncio.sleep(0.1)
        
        # Calculate final metrics
        if response_times:
            stress_results["avg_response_time"] = statistics.mean(response_times)
            stress_results["max_response_time"] = max(response_times)
            stress_results["min_response_time"] = min(response_times)
        
        stress_results["requests_per_second"] = stress_results["total_requests"] / stress_results["duration_seconds"]
        stress_results["success_rate"] = (stress_results["successful_requests"] / stress_results["total_requests"]) * 100
        
        print(f"  📊 Stress Test Results:")
        print(f"    Total Requests: {stress_results['total_requests']}")
        print(f"    Successful: {stress_results['successful_requests']}")
        print(f"    Failed: {stress_results['failed_requests']}")
        print(f"    Success Rate: {stress_results['success_rate']:.1f}%")
        print(f"    RPS: {stress_results['requests_per_second']:.2f}")
        print(f"    Avg Response Time: {stress_results['avg_response_time']:.2f}ms")
        
        self.results["stress_testing"] = stress_results
    
    async def benchmark_reliability(self):
        """Benchmark 8: Reliability Testing"""
        print("\n8️⃣ Testing System Reliability...")
        
        reliability_results = {
            "uptime_test_duration": 300,  # 5 minutes
            "health_check_interval": 5,   # Every 5 seconds
            "total_health_checks": 0,
            "successful_health_checks": 0,
            "failed_health_checks": 0,
            "uptime_percentage": 0,
            "longest_downtime": 0,
            "current_downtime": 0
        }
        
        start_time = time.time()
        last_successful_check = start_time
        current_downtime_start = None
        
        async with httpx.AsyncClient(timeout=10) as client:
            while (time.time() - start_time) < reliability_results["uptime_test_duration"]:
                check_start = time.time()
                try:
                    response = await client.get(f"{self.base_url}/health")
                    check_end = time.time()
                    
                    reliability_results["total_health_checks"] += 1
                    
                    if response.status_code == 200:
                        reliability_results["successful_health_checks"] += 1
                        last_successful_check = check_end
                        
                        # End current downtime if any
                        if current_downtime_start:
                            downtime_duration = check_end - current_downtime_start
                            reliability_results["longest_downtime"] = max(
                                reliability_results["longest_downtime"], 
                                downtime_duration
                            )
                            current_downtime_start = None
                    else:
                        reliability_results["failed_health_checks"] += 1
                        if not current_downtime_start:
                            current_downtime_start = check_start
                            
                except Exception as e:
                    reliability_results["total_health_checks"] += 1
                    reliability_results["failed_health_checks"] += 1
                    if not current_downtime_start:
                        current_downtime_start = check_start
                
                # Wait for next check
                await asyncio.sleep(reliability_results["health_check_interval"])
        
        # Calculate final metrics
        reliability_results["uptime_percentage"] = (
            reliability_results["successful_health_checks"] / 
            reliability_results["total_health_checks"]
        ) * 100
        
        if current_downtime_start:
            reliability_results["current_downtime"] = time.time() - current_downtime_start
        
        print(f"  📊 Reliability Test Results:")
        print(f"    Total Health Checks: {reliability_results['total_health_checks']}")
        print(f"    Successful: {reliability_results['successful_health_checks']}")
        print(f"    Failed: {reliability_results['failed_health_checks']}")
        print(f"    Uptime: {reliability_results['uptime_percentage']:.1f}%")
        print(f"    Longest Downtime: {reliability_results['longest_downtime']:.1f}s")
        
        self.results["reliability"] = reliability_results
    
    def percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of a dataset"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    async def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("=" * 60)
        
        total_time = time.time() - self.start_time
        
        print(f"🎯 BENCHMARK SUMMARY:")
        print(f"   Total Duration: {total_time:.2f}s")
        print(f"   Tests Completed: {len(self.results)}")
        
        # Performance Assessment
        print(f"\n📈 PERFORMANCE ASSESSMENT:")
        
        # API Response Times Assessment
        if "api_response_times" in self.results:
            health_avg = self.results["api_response_times"].get("Health Check", {}).get("avg", 0)
            if health_avg < 100:
                print("  🟢 API Response Times: EXCELLENT (<100ms)")
            elif health_avg < 500:
                print("  🟡 API Response Times: GOOD (<500ms)")
            else:
                print("  🔴 API Response Times: NEEDS IMPROVEMENT (>500ms)")
        
        # Concurrent Requests Assessment
        if "concurrent_requests" in self.results:
            max_concurrency = max(self.results["concurrent_requests"].keys())
            max_success_rate = self.results["concurrent_requests"][max_concurrency]["success_rate"]
            if max_success_rate >= 95:
                print("  🟢 Concurrent Handling: EXCELLENT (>95% success)")
            elif max_success_rate >= 90:
                print("  🟡 Concurrent Handling: GOOD (>90% success)")
            else:
                print("  🔴 Concurrent Handling: NEEDS IMPROVEMENT (<90% success)")
        
        # Memory Usage Assessment
        if "memory_usage" in self.results:
            memory_growth = self.results["memory_usage"]["memory_growth_mb"]
            if memory_growth < 50:
                print("  🟢 Memory Usage: EXCELLENT (<50MB growth)")
            elif memory_growth < 100:
                print("  🟡 Memory Usage: GOOD (<100MB growth)")
            else:
                print("  🔴 Memory Usage: NEEDS IMPROVEMENT (>100MB growth)")
        
        # Reliability Assessment
        if "reliability" in self.results:
            uptime = self.results["reliability"]["uptime_percentage"]
            if uptime >= 99:
                print("  🟢 Reliability: EXCELLENT (>99% uptime)")
            elif uptime >= 95:
                print("  🟡 Reliability: GOOD (>95% uptime)")
            else:
                print("  🔴 Reliability: NEEDS IMPROVEMENT (<95% uptime)")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_time,
            "results": self.results
        }
        
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print("=" * 60)

# Pytest benchmarks
@pytest.mark.benchmark
def test_api_health_benchmark(benchmark):
    """Benchmark API health endpoint"""
    async def health_check():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            return response.status_code == 200
    
    result = benchmark(asyncio.run, health_check())
    assert result

@pytest.mark.benchmark
def test_search_benchmark(benchmark):
    """Benchmark search endpoint"""
    async def search_query():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/search",
                json={"query": "test query", "limit": 10}
            )
            return response.status_code == 200
    
    result = benchmark(asyncio.run, search_query())
    assert result

# Main execution
async def main():
    """Main execution function"""
    print("⚡ OBSIDIAN VAULT AI SYSTEM - PERFORMANCE BENCHMARK")
    print("Version: 3.0.0 - Production Ready")
    print("=" * 60)
    
    # Check if API is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print(f"❌ API not healthy: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure the vault-api server is running on localhost:8080")
        return False
    
    # Run performance benchmarks
    test_suite = PerformanceTestSuite()
    results = await test_suite.run_all_benchmarks()
    
    return True

if __name__ == "__main__":
    print("🧪 Starting Performance Benchmark Suite...")
    print("Make sure your vault-api server is running on localhost:8080")
    print()
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 Performance benchmarks completed successfully!")
        exit(0)
    else:
        print("\n❌ Performance benchmarks failed. Check the output above for details.")
        exit(1)

