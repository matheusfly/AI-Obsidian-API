#!/usr/bin/env python3
"""
Test Suite for Enterprise-Grade Polish Features
Tests structured logging, metrics collection, and admin dashboard
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.logging.structured_logger import (
    StructuredLogger, log_query_start, log_search_start, 
    log_search_completed, log_gemini_start, log_gemini_completed,
    log_query_completed, get_analytics
)
from src.logging.metrics_collector import MetricsCollector, metrics_collector
from src.admin.api import app
from fastapi.testclient import TestClient

class EnterprisePolishTester:
    """Test suite for enterprise polish features"""
    
    def __init__(self):
        self.logger = StructuredLogger("test_service")
        self.metrics_collector = metrics_collector  # Use global instance
        self.test_client = TestClient(app)
        self.test_results = []
    
    async def test_structured_logging(self):
        """Test structured logging functionality"""
        print("🧪 Testing Structured Logging...")
        
        try:
            # Test query logging
            query_context = log_query_start("test query", max_results=5, user_id="test_user")
            assert "query" in query_context
            assert query_context["query"] == "test query"
            print("✅ Query start logging works")
            
            # Test search logging
            search_context = log_search_start("test query", "semantic")
            assert search_context["search_method"] == "semantic"
            print("✅ Search start logging works")
            
            # Test search completion logging
            similarity_scores = [0.8, 0.7, 0.6]
            search_complete = log_search_completed(
                "test query", 3, 150.5, "semantic", similarity_scores
            )
            assert search_complete["results_count"] == 3
            # Check if avg_similarity is calculated correctly (should be 0.7)
            expected_avg = sum(similarity_scores) / len(similarity_scores)
            assert search_complete["avg_similarity"] == expected_avg
            print("✅ Search completion logging works")
            
            # Test Gemini logging
            gemini_start = log_gemini_start("test query", 3)
            assert gemini_start["context_chunks"] == 3
            print("✅ Gemini start logging works")
            
            gemini_complete = log_gemini_completed("test query", 500, 200.0, 100)
            assert gemini_complete["response_length"] == 500
            assert gemini_complete["token_count"] == 100
            print("✅ Gemini completion logging works")
            
            # Test query completion logging
            query_complete = log_query_completed("test query", 350.5, success=True)
            assert query_complete["total_time_ms"] == 350.5
            assert query_complete["success"] == True
            print("✅ Query completion logging works")
            
            # Test error logging
            try:
                raise ValueError("Test error")
            except Exception as e:
                error_context = self.logger.log_error(e, {"test": "context"})
                assert error_context["error_type"] == "ValueError"
                print("✅ Error logging works")
            
            self.test_results.append(("Structured Logging", "PASS"))
            return True
            
        except Exception as e:
            import traceback
            print(f"❌ Structured logging test failed: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            self.test_results.append(("Structured Logging", f"FAIL: {e}"))
            return False
    
    async def test_metrics_collection(self):
        """Test metrics collection functionality"""
        print("🧪 Testing Metrics Collection...")
        
        try:
            # Test system metrics collection
            metrics = self.metrics_collector.get_system_metrics()
            assert hasattr(metrics, 'cpu_percent')
            assert hasattr(metrics, 'memory_percent')
            assert hasattr(metrics, 'disk_usage_percent')
            print("✅ System metrics collection works")
            
            # Test query metrics collection
            self.metrics_collector.add_query_metrics(
                "test query", 100.0, 200.0, 300.0, 5, True
            )
            recent_queries = self.metrics_collector.get_recent_query_metrics(1)
            assert len(recent_queries) >= 1
            assert recent_queries[0].query == "test query"
            print("✅ Query metrics collection works")
            
            # Test analytics summary
            analytics = self.metrics_collector.get_analytics_summary()
            assert "uptime_seconds" in analytics
            assert "total_queries" in analytics
            assert "success_rate" in analytics
            print("✅ Analytics summary works")
            
            # Test metrics export
            export_file = self.metrics_collector.export_metrics("logs/test_metrics.json")
            assert export_file is not None
            assert Path(export_file).exists()
            print("✅ Metrics export works")
            
            self.test_results.append(("Metrics Collection", "PASS"))
            return True
            
        except Exception as e:
            print(f"❌ Metrics collection test failed: {e}")
            self.test_results.append(("Metrics Collection", f"FAIL: {e}"))
            return False
    
    async def test_admin_dashboard_api(self):
        """Test admin dashboard API endpoints"""
        print("🧪 Testing Admin Dashboard API...")
        
        try:
            # Test status endpoint
            status_response = self.test_client.get("/api/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "healthy"
            print("✅ Status endpoint works")
            
            # Test health endpoint
            health_response = self.test_client.get("/api/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert "status" in health_data
            assert "health_score" in health_data
            print("✅ Health endpoint works")
            
            # Test analytics endpoint
            analytics_response = self.test_client.get("/api/analytics")
            print(f"Analytics response status: {analytics_response.status_code}")
            if analytics_response.status_code != 200:
                print(f"Analytics response content: {analytics_response.text}")
                # Let's also test the metrics collector directly
                print("Testing metrics collector directly...")
                analytics_data = self.metrics_collector.get_analytics_summary()
                print(f"Analytics data keys: {list(analytics_data.keys())}")
                print(f"Analytics data: {analytics_data}")
            assert analytics_response.status_code == 200
            analytics_data = analytics_response.json()
            assert "uptime_seconds" in analytics_data
            assert "total_queries" in analytics_data
            print("✅ Analytics endpoint works")
            
            # Test recent queries endpoint
            queries_response = self.test_client.get("/api/queries/recent")
            assert queries_response.status_code == 200
            queries_data = queries_response.json()
            assert isinstance(queries_data, list)
            print("✅ Recent queries endpoint works")
            
            # Test system metrics endpoint
            metrics_response = self.test_client.get("/api/metrics/system")
            assert metrics_response.status_code == 200
            metrics_data = metrics_response.json()
            assert isinstance(metrics_data, list)
            print("✅ System metrics endpoint works")
            
            # Test dashboard data endpoint
            dashboard_response = self.test_client.get("/api/dashboard")
            assert dashboard_response.status_code == 200
            dashboard_data = dashboard_response.json()
            assert "system_health" in dashboard_data
            assert "analytics" in dashboard_data
            print("✅ Dashboard data endpoint works")
            
            # Test metrics export endpoint
            export_response = self.test_client.post("/api/metrics/export")
            assert export_response.status_code == 200
            export_data = export_response.json()
            assert export_data["status"] == "success"
            print("✅ Metrics export endpoint works")
            
            self.test_results.append(("Admin Dashboard API", "PASS"))
            return True
            
        except Exception as e:
            import traceback
            print(f"❌ Admin dashboard API test failed: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            self.test_results.append(("Admin Dashboard API", f"FAIL: {e}"))
            return False
    
    async def test_integration(self):
        """Test integration between logging and metrics"""
        print("🧪 Testing Integration...")
        
        try:
            # Simulate a complete query workflow
            query = "integration test query"
            
            # Start query
            log_query_start(query, max_results=5)
            
            # Simulate search
            await asyncio.sleep(0.1)  # Simulate search time
            log_search_start(query, "semantic")
            await asyncio.sleep(0.1)
            log_search_completed(query, 3, 100.0, "semantic", [0.8, 0.7, 0.6])
            
            # Simulate Gemini processing
            log_gemini_start(query, 3)
            await asyncio.sleep(0.1)
            log_gemini_completed(query, 400, 100.0, 50)
            
            # Complete query
            log_query_completed(query, 200.0, success=True)
            
            # Add to metrics collector
            self.metrics_collector.add_query_metrics(
                query, 100.0, 100.0, 200.0, 3, True
            )
            
            # Verify integration
            analytics = get_analytics()
            assert analytics["total_queries"] >= 1
            assert analytics["success_rate"] >= 0
            
            print("✅ Integration test works")
            self.test_results.append(("Integration", "PASS"))
            return True
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            self.test_results.append(("Integration", f"FAIL: {e}"))
            return False
    
    async def run_all_tests(self):
        """Run all enterprise polish tests"""
        print("🚀 Starting Enterprise Polish Test Suite...")
        print("=" * 60)
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Run tests
        tests = [
            self.test_structured_logging(),
            self.test_metrics_collection(),
            self.test_admin_dashboard_api(),
            self.test_integration()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for i, result in enumerate(results):
            test_name = ["Structured Logging", "Metrics Collection", "Admin Dashboard API", "Integration"][i]
            if isinstance(result, Exception):
                print(f"❌ {test_name}: FAIL - {result}")
                failed += 1
            elif result:
                print(f"✅ {test_name}: PASS")
                passed += 1
            else:
                print(f"❌ {test_name}: FAIL")
                failed += 1
        
        print(f"\n📈 Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! Enterprise polish features are working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        return failed == 0

async def main():
    """Main test function"""
    tester = EnterprisePolishTester()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
