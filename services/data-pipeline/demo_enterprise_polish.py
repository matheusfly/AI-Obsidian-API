#!/usr/bin/env python3
"""
Enterprise Polish Features Demo
Demonstrates structured logging, metrics collection, and admin dashboard
"""

import asyncio
import time
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.logging.structured_logger import (
    log_query_start, log_search_start, log_search_completed,
    log_gemini_start, log_gemini_completed, log_query_completed,
    get_analytics
)
from src.logging.metrics_collector import metrics_collector

async def demo_enterprise_polish():
    """Demonstrate enterprise polish features"""
    print("🚀 Data Vault Obsidian - Enterprise Polish Features Demo")
    print("=" * 60)
    
    # Start metrics collection
    metrics_collector.start_collection()
    print("📊 Started metrics collection")
    
    # Simulate some queries with full logging
    queries = [
        "machine learning algorithms",
        "API authentication implementation", 
        "database optimization techniques",
        "Python performance tuning",
        "vector database configuration"
    ]
    
    print(f"\n🔍 Simulating {len(queries)} queries with enterprise logging...")
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        # Start query logging
        query_context = log_query_start(query, max_results=5, user_id=f"demo_user_{i}")
        print(f"✅ Query started: {query_context['operation']}")
        
        # Simulate search phase
        await asyncio.sleep(0.1)  # Simulate search time
        search_context = log_search_start(query, "semantic")
        print(f"🔍 Search started: {search_context['search_method']}")
        
        # Simulate search completion
        await asyncio.sleep(0.05)  # Simulate search completion
        similarity_scores = [0.8 + (i * 0.02), 0.7 + (i * 0.01), 0.6 + (i * 0.01)]
        search_complete = log_search_completed(
            query, 3, 50.0 + (i * 10), "semantic", similarity_scores
        )
        print(f"✅ Search completed: {search_complete['results_count']} results, "
              f"avg similarity: {search_complete['avg_similarity']:.3f}")
        
        # Simulate Gemini processing
        gemini_start = log_gemini_start(query, 3)
        print(f"🤖 Gemini started: {gemini_start['context_chunks']} context chunks")
        
        await asyncio.sleep(0.1)  # Simulate Gemini processing
        gemini_complete = log_gemini_completed(query, 300 + (i * 50), 100.0 + (i * 20), 50 + (i * 10))
        print(f"✅ Gemini completed: {gemini_complete['response_length']} chars, "
              f"{gemini_complete['token_count']} tokens")
        
        # Complete query
        total_time = 150.0 + (i * 30)
        query_complete = log_query_completed(query, total_time, success=True)
        print(f"🎯 Query completed: {query_complete['total_time_ms']:.1f}ms total")
        
        # Add to metrics collector
        metrics_collector.add_query_metrics(
            query, 50.0 + (i * 10), 100.0 + (i * 20), total_time, 3, True
        )
        
        print(f"📊 Added to metrics collector")
    
    # Show analytics
    print("\n" + "=" * 60)
    print("📈 ANALYTICS SUMMARY")
    print("=" * 60)
    
    analytics = get_analytics()
    print(f"⏱️  Uptime: {analytics['uptime_seconds']:.1f} seconds")
    print(f"🔢 Total Queries: {analytics['total_queries']}")
    print(f"✅ Success Rate: {analytics['success_rate']:.1f}%")
    print(f"⚡ Avg Search Time: {analytics['avg_search_time_ms']:.1f}ms")
    print(f"🤖 Avg Gemini Time: {analytics['avg_gemini_time_ms']:.1f}ms")
    print(f"🎯 Avg Total Time: {analytics.get('avg_total_time_ms', 0):.1f}ms")
    
    # Show system metrics
    system_metrics = analytics.get('system_metrics', {})
    print(f"\n💻 SYSTEM METRICS")
    print(f"🖥️  CPU Usage: {system_metrics.get('avg_cpu_percent', 0):.1f}%")
    print(f"🧠 Memory Usage: {system_metrics.get('avg_memory_percent', 0):.1f}%")
    print(f"💾 Disk Usage: {system_metrics.get('avg_disk_usage_percent', 0):.1f}%")
    
    # Show query trends
    query_trends = analytics.get('query_trends', {})
    print(f"\n📊 QUERY TRENDS")
    print(f"🚀 Queries/Minute: {query_trends.get('queries_per_minute', 0):.2f}")
    print(f"📋 Avg Results/Query: {query_trends.get('avg_results_per_query', 0):.1f}")
    print(f"❌ Error Rate: {query_trends.get('error_rate', 0):.1f}%")
    
    # Export metrics
    print(f"\n💾 EXPORTING METRICS...")
    export_file = metrics_collector.export_metrics("logs/demo_metrics.json")
    if export_file:
        print(f"✅ Metrics exported to: {export_file}")
    
    print(f"\n🌐 ADMIN DASHBOARD")
    print(f"📊 Dashboard URL: http://localhost:8000")
    print(f"🔗 API Health: http://localhost:8000/api/health")
    print(f"📈 API Analytics: http://localhost:8000/api/analytics")
    print(f"🔍 API Queries: http://localhost:8000/api/queries/recent")
    
    print(f"\n🎉 Enterprise polish features demonstration complete!")
    print(f"💡 To start the admin dashboard, run: python launch_admin_dashboard.py")

if __name__ == "__main__":
    asyncio.run(demo_enterprise_polish())
