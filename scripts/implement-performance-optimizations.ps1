# Performance Optimization Implementation Script
# Implements specific optimizations based on usage patterns

param(
    [switch]$DryRun = $false,
    [switch]$Verbose = $false
)

Write-Host "🚀 Implementing Performance Optimizations..." -ForegroundColor Green

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
}

# 1. OPTIMIZE PROMETHEUS SCRAPING FREQUENCY
Write-Host "📊 Optimizing Prometheus scraping frequency..." -ForegroundColor Cyan

$prometheusConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'data-pipeline'
    static_configs:
      - targets: ['data-pipeline:8003']
    scrape_interval: 30s  # Increased from 15s to 30s
    scrape_timeout: 10s   # Added timeout
    metrics_path: '/metrics'
    scheme: 'http'
    
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']
    scrape_interval: 30s
    scrape_timeout: 10s
    metrics_path: '/metrics'
    scheme: 'http'
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
    scrape_timeout: 10s
"@

if (-not $DryRun) {
    $prometheusConfig | Out-File -FilePath "config/prometheus-optimized.yml" -Encoding UTF8
    Write-Host "✅ Prometheus config optimized" -ForegroundColor Green
} else {
    Write-Host "🔍 Would create: config/prometheus-optimized.yml" -ForegroundColor Yellow
}

# 2. CREATE CACHE OPTIMIZATION CONFIG
Write-Host "🗄️ Creating cache optimization config..." -ForegroundColor Cyan

$cacheConfig = @"
# Cache Optimization Configuration
CACHE_CONFIG = {
    "embedding_cache": {
        "max_size": 1000,        # Limit cache entries
        "ttl": 3600,            # 1 hour TTL
        "eviction_policy": "lru", # Least Recently Used
        "cleanup_interval": 300   # Clean up every 5 minutes
    },
    "query_cache": {
        "max_size": 500,
        "ttl": 1800,            # 30 minutes TTL
        "eviction_policy": "lru",
        "cleanup_interval": 300
    },
    "search_cache": {
        "max_size": 200,
        "ttl": 900,             # 15 minutes TTL
        "eviction_policy": "lru",
        "cleanup_interval": 300
    }
}
"@

if (-not $DryRun) {
    $cacheConfig | Out-File -FilePath "config/cache-optimization.py" -Encoding UTF8
    Write-Host "✅ Cache optimization config created" -ForegroundColor Green
} else {
    Write-Host "🔍 Would create: config/cache-optimization.py" -ForegroundColor Yellow
}

# 3. CREATE MEMORY OPTIMIZATION SCRIPT
Write-Host "💾 Creating memory optimization script..." -ForegroundColor Cyan

$memoryOptimizationScript = @"
# Memory Optimization Script
import gc
import psutil
import asyncio
from typing import Dict, Any
import weakref

class MemoryOptimizer:
    def __init__(self):
        self.cleanup_interval = 300  # 5 minutes
        self.memory_threshold = 0.8  # 80% memory usage
        self.weak_refs = weakref.WeakValueDictionary()
    
    async def optimize_memory(self):
        """Optimize memory usage based on current patterns"""
        memory_info = psutil.virtual_memory()
        
        if memory_info.percent > (self.memory_threshold * 100):
            print(f"⚠️ High memory usage: {memory_info.percent}%")
            await self.cleanup_memory()
        else:
            print(f"✅ Memory usage normal: {memory_info.percent}%")
    
    async def cleanup_memory(self):
        """Clean up memory-intensive objects"""
        # Force garbage collection
        gc.collect()
        
        # Clear weak references
        self.weak_refs.clear()
        
        print("🧹 Memory cleanup completed")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get detailed memory statistics"""
        memory_info = psutil.virtual_memory()
        process = psutil.Process()
        
        return {
            "total_memory_mb": memory_info.total / 1024 / 1024,
            "available_memory_mb": memory_info.available / 1024 / 1024,
            "used_memory_mb": memory_info.used / 1024 / 1024,
            "memory_percent": memory_info.percent,
            "process_memory_mb": process.memory_info().rss / 1024 / 1024,
            "process_memory_percent": process.memory_percent()
        }

# Usage example
async def main():
    optimizer = MemoryOptimizer()
    await optimizer.optimize_memory()
    stats = optimizer.get_memory_stats()
    print(f"Memory Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
"@

if (-not $DryRun) {
    $memoryOptimizationScript | Out-File -FilePath "scripts/memory-optimizer.py" -Encoding UTF8
    Write-Host "✅ Memory optimization script created" -ForegroundColor Green
} else {
    Write-Host "🔍 Would create: scripts/memory-optimizer.py" -ForegroundColor Yellow
}

# 4. CREATE HTTP OPTIMIZATION MIDDLEWARE
Write-Host "🌐 Creating HTTP optimization middleware..." -ForegroundColor Cyan

$httpOptimizationScript = @"
# HTTP Optimization Middleware
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import gzip
import time
from typing import Callable

class HTTPOptimizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, compress_threshold: int = 1024):
        super().__init__(app)
        self.compress_threshold = compress_threshold
        self.request_times = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Track request start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Cache-Control"] = "public, max-age=300"
        
        # Compress large responses
        if (response.headers.get("content-type", "").startswith("application/json") and 
            len(response.body) > self.compress_threshold):
            
            compressed_body = gzip.compress(response.body)
            response.body = compressed_body
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed_body))
        
        # Add CORS headers for better performance
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response

# Usage in main.py
# app.add_middleware(HTTPOptimizationMiddleware, compress_threshold=1024)
"@

if (-not $DryRun) {
    $httpOptimizationScript | Out-File -FilePath "scripts/http-optimization-middleware.py" -Encoding UTF8
    Write-Host "✅ HTTP optimization middleware created" -ForegroundColor Green
} else {
    Write-Host "🔍 Would create: scripts/http-optimization-middleware.py" -ForegroundColor Yellow
}

# 5. CREATE FAVICON FIX
Write-Host "🔧 Creating favicon fix..." -ForegroundColor Cyan

$faviconFix = @"
# Add to main.py
from fastapi.responses import FileResponse
import os

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    favicon_path = "static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        # Return a minimal 1x1 pixel favicon
        return Response(
            content=b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00\x68\x04\x00\x00\x16\x00\x00\x00',
            media_type="image/x-icon"
        )
"@

if (-not $DryRun) {
    $faviconFix | Out-File -FilePath "scripts/favicon-fix.py" -Encoding UTF8
    Write-Host "✅ Favicon fix created" -ForegroundColor Green
} else {
    Write-Host "🔍 Would create: scripts/favicon-fix.py" -ForegroundColor Yellow
}

# 6. CREATE PERFORMANCE MONITORING SCRIPT
Write-Host "📊 Creating performance monitoring script..." -ForegroundColor Cyan

$performanceMonitoringScript = @"
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
"@

if (-not $DryRun) {
    $performanceMonitoringScript | Out-File -FilePath "scripts/performance-monitor.py" -Encoding UTF8
    Write-Host "✅ Performance monitoring script created" -ForegroundColor Green
} else {
    Write-Host "🔍 Would create: scripts/performance-monitor.py" -ForegroundColor Yellow
}

# Summary
Write-Host "`n🎉 Performance Optimization Implementation Complete!" -ForegroundColor Green
Write-Host "`n📋 Created Files:" -ForegroundColor Cyan
Write-Host "   • config/prometheus-optimized.yml - Reduced scraping frequency" -ForegroundColor White
Write-Host "   • config/cache-optimization.py - Cache size limits and TTL" -ForegroundColor White
Write-Host "   • scripts/memory-optimizer.py - Memory cleanup and optimization" -ForegroundColor White
Write-Host "   • scripts/http-optimization-middleware.py - Response compression" -ForegroundColor White
Write-Host "   • scripts/favicon-fix.py - Fix 404 favicon errors" -ForegroundColor White
Write-Host "   • scripts/performance-monitor.py - Performance analysis" -ForegroundColor White

Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Review the created files" -ForegroundColor White
Write-Host "   2. Apply optimizations to your services" -ForegroundColor White
Write-Host "   3. Run performance monitoring script" -ForegroundColor White
Write-Host "   4. Monitor improvements in Grafana" -ForegroundColor White

if ($DryRun) {
    Write-Host "`n🔍 This was a dry run - no files were actually created" -ForegroundColor Yellow
}
