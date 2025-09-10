#!/usr/bin/env python3
"""
Debug script for admin dashboard issues
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.logging.metrics_collector import metrics_collector
from src.admin.api import get_system_health, get_analytics, get_recent_queries, get_system_metrics_history
from src.admin.models import DashboardData
from datetime import datetime
import asyncio

async def debug_dashboard():
    """Debug dashboard data retrieval"""
    print("🔍 Debugging dashboard data retrieval...")
    
    try:
        print("1. Testing metrics collector...")
        analytics = metrics_collector.get_analytics_summary()
        print(f"   ✅ Analytics: {list(analytics.keys())}")
        
        print("2. Testing system health...")
        health = await get_system_health()
        print(f"   ✅ Health: {health.status}")
        
        print("3. Testing analytics endpoint...")
        analytics_data = await get_analytics()
        print(f"   ✅ Analytics endpoint: {analytics_data.uptime_seconds}")
        
        print("4. Testing recent queries...")
        queries = await get_recent_queries(60, 50)
        print(f"   ✅ Recent queries: {len(queries)} queries")
        
        print("5. Testing system metrics...")
        metrics = await get_system_metrics_history(60)
        print(f"   ✅ System metrics: {len(metrics)} metrics")
        
        print("6. Testing dashboard data assembly...")
        dashboard_data = DashboardData(
            system_health=health,
            analytics=analytics_data,
            recent_queries=queries,
            system_metrics_history=metrics,
            alerts=[],
            last_updated=datetime.utcnow()
        )
        print(f"   ✅ Dashboard data: {dashboard_data.last_updated}")
        
        print("🎉 All tests passed! Dashboard should work.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_dashboard())
