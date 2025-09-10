# Performance Monitoring Script
import asyncio
import aiohttp
import json
from datetime import datetime
import time

class PerformanceMonitor:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
        self.metrics = []
    
    async def collect_metrics(self):
        """Collect performance metrics from all endpoints"""
        async with aiohttp.ClientSession() as session:
            endpoints = [
                "/health",
                "/metrics",
                "/search",
                "/query"
            ]
            
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        response_time = time.time() - start_time
                        
                        metric = {
                            "endpoint": endpoint,
                            "status_code": response.status,
                            "response_time": response_time,
                            "timestamp": datetime.now().isoformat(),
                            "content_length": len(await response.text()) if response.status == 200 else 0
                        }
                        
                        self.metrics.append(metric)
                        print(f"✅ {endpoint}: {response.status} ({response_time:.3f}s)")
                        
                except Exception as e:
                    print(f"❌ {endpoint}: Error - {e}")
    
    def analyze_performance(self):
        """Analyze collected metrics and provide optimization recommendations"""
        if not self.metrics:
            print("No metrics collected")
            return
        
        # Calculate averages
        avg_response_time = sum(m["response_time"] for m in self.metrics) / len(self.metrics)
        status_codes = [m["status_code"] for m in self.metrics]
        success_rate = (status_codes.count(200) / len(status_codes)) * 100
        
        print(f"\n📊 Performance Analysis:")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Requests: {len(self.metrics)}")
        
        # Optimization recommendations
        print(f"\n🎯 Optimization Recommendations:")
        
        if avg_response_time > 0.5:
            print("   ⚠️ High response time - consider caching")
        
        if success_rate < 95:
            print("   ⚠️ Low success rate - check error handling")
        
        slow_endpoints = [m for m in self.metrics if m["response_time"] > 1.0]
        if slow_endpoints:
            print(f"   ⚠️ Slow endpoints: {[m['endpoint'] for m in slow_endpoints]}")
        
        print("   ✅ Consider implementing the optimizations from the script")

async def main():
    monitor = PerformanceMonitor()
    await monitor.collect_metrics()
    monitor.analyze_performance()

if __name__ == "__main__":
    asyncio.run(main())
