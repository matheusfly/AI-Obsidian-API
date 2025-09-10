#!/usr/bin/env python3
"""
Admin Dashboard API for Data Vault Obsidian
FastAPI endpoints for system monitoring and analytics
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Optional
import asyncio
from datetime import datetime, timedelta
import json
from pathlib import Path

from .models import (
    SystemHealth, AnalyticsSummary, QueryMetrics, SystemMetrics,
    DashboardData, HealthAlert, QueryTrends
)
from ..logging.metrics_collector import metrics_collector
from ..logging.structured_logger import get_analytics

# Initialize FastAPI app
app = FastAPI(
    title="Data Vault Obsidian Admin Dashboard",
    description="Enterprise monitoring and analytics dashboard",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for caching
_cached_health: Optional[SystemHealth] = None
_cached_analytics: Optional[AnalyticsSummary] = None
_cached_queries: List[QueryMetrics] = []
_last_update = datetime.utcnow()

@app.on_event("startup")
async def startup_event():
    """Initialize metrics collection on startup"""
    metrics_collector.start_collection()
    print("🚀 Admin Dashboard started - Metrics collection active")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop metrics collection on shutdown"""
    metrics_collector.stop_collection()
    print("🛑 Admin Dashboard stopped - Metrics collection stopped")

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard page"""
    try:
        # Try to serve from frontend build directory
        frontend_path = Path("frontend/admin-dashboard/dist/index.html")
        if frontend_path.exists():
            return HTMLResponse(content=frontend_path.read_text())
        else:
            # Fallback to simple HTML
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Data Vault Obsidian Admin Dashboard</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .header { text-align: center; margin-bottom: 30px; }
                    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
                    .metric-card { background: #f8f9fa; padding: 20px; border-radius: 6px; border-left: 4px solid #007bff; }
                    .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
                    .metric-label { color: #666; margin-top: 5px; }
                    .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
                    .status.healthy { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .status.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
                    .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                    .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
                    .refresh-btn:hover { background: #0056b3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Data Vault Obsidian Admin Dashboard</h1>
                        <p>Enterprise monitoring and analytics dashboard</p>
                        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
                    </div>
                    
                    <div id="dashboard-content">
                        <div class="status healthy">
                            <strong>System Status:</strong> Loading...
                        </div>
                        
                        <div class="metrics">
                            <div class="metric-card">
                                <div class="metric-value" id="uptime">-</div>
                                <div class="metric-label">Uptime (seconds)</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="queries">-</div>
                                <div class="metric-label">Total Queries</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="success-rate">-</div>
                                <div class="metric-label">Success Rate (%)</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="avg-time">-</div>
                                <div class="metric-label">Avg Response Time (ms)</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <script>
                    async function loadDashboard() {
                        try {
                            const response = await fetch('/api/dashboard');
                            const data = await response.json();
                            
                            document.getElementById('uptime').textContent = Math.round(data.analytics.uptime_seconds);
                            document.getElementById('queries').textContent = data.analytics.total_queries;
                            document.getElementById('success-rate').textContent = Math.round(data.analytics.success_rate);
                            document.getElementById('avg-time').textContent = Math.round(data.analytics.avg_total_time_ms);
                            
                            const statusEl = document.querySelector('.status');
                            if (data.system_health.health_score >= 80) {
                                statusEl.className = 'status healthy';
                                statusEl.innerHTML = '<strong>System Status:</strong> Healthy';
                            } else if (data.system_health.health_score >= 60) {
                                statusEl.className = 'status warning';
                                statusEl.innerHTML = '<strong>System Status:</strong> Warning';
                            } else {
                                statusEl.className = 'status error';
                                statusEl.innerHTML = '<strong>System Status:</strong> Error';
                            }
                        } catch (error) {
                            console.error('Error loading dashboard:', error);
                        }
                    }
                    
                    // Load dashboard on page load
                    loadDashboard();
                    
                    // Auto-refresh every 30 seconds
                    setInterval(loadDashboard, 30000);
                </script>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading dashboard: {str(e)}</h1>")

@app.get("/api/health", response_model=SystemHealth)
async def get_system_health():
    """Get current system health status"""
    try:
        current_metrics = metrics_collector.get_system_metrics()
        analytics = metrics_collector.get_analytics_summary()
        
        # Calculate health score based on various factors
        health_score = 100.0
        alerts = []
        
        # CPU health check
        if current_metrics.cpu_percent > 90:
            health_score -= 20
            alerts.append("High CPU usage detected")
        elif current_metrics.cpu_percent > 80:
            health_score -= 10
            alerts.append("Elevated CPU usage")
        
        # Memory health check
        if current_metrics.memory_percent > 95:
            health_score -= 25
            alerts.append("Critical memory usage")
        elif current_metrics.memory_percent > 85:
            health_score -= 15
            alerts.append("High memory usage")
        
        # Disk health check
        if current_metrics.disk_usage_percent > 95:
            health_score -= 20
            alerts.append("Critical disk usage")
        elif current_metrics.disk_usage_percent > 85:
            health_score -= 10
            alerts.append("High disk usage")
        
        # Query success rate health check
        if analytics["success_rate"] < 95:
            health_score -= 15
            alerts.append("Low query success rate")
        
        # Determine overall status
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        else:
            status = "error"
        
        return SystemHealth(
            status=status,
            uptime_seconds=analytics["uptime_seconds"],
            current_metrics=SystemMetrics(**current_metrics.__dict__),
            health_score=max(0, health_score),
            alerts=alerts,
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system health: {str(e)}")

@app.get("/api/analytics", response_model=AnalyticsSummary)
async def get_analytics():
    """Get comprehensive analytics summary"""
    try:
        analytics = metrics_collector.get_analytics_summary()
        return AnalyticsSummary(**analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@app.get("/api/queries/recent", response_model=List[QueryMetrics])
async def get_recent_queries(minutes: int = 60, limit: int = 100):
    """Get recent query metrics"""
    try:
        recent_queries = metrics_collector.get_recent_query_metrics(minutes)
        # Convert to QueryMetrics objects and limit results
        query_metrics = [QueryMetrics(**q.__dict__) for q in recent_queries[-limit:]]
        return query_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recent queries: {str(e)}")

@app.get("/api/metrics/system", response_model=List[SystemMetrics])
async def get_system_metrics_history(minutes: int = 60):
    """Get system metrics history"""
    try:
        recent_metrics = metrics_collector.get_recent_system_metrics(minutes)
        return [SystemMetrics(**m.__dict__) for m in recent_metrics]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system metrics: {str(e)}")

@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """Get complete dashboard data"""
    try:
        # Get all data in parallel
        health_task = asyncio.create_task(get_system_health())
        analytics_task = asyncio.create_task(get_analytics())
        queries_task = asyncio.create_task(get_recent_queries(60, 50))
        metrics_task = asyncio.create_task(get_system_metrics_history(60))
        
        # Wait for all tasks to complete
        health, analytics, queries, metrics = await asyncio.gather(
            health_task, analytics_task, queries_task, metrics_task
        )
        
        return DashboardData(
            system_health=health,
            analytics=analytics,
            recent_queries=queries,
            system_metrics_history=metrics,
            alerts=[],  # TODO: Implement alert system
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard data: {str(e)}")

@app.post("/api/metrics/export")
async def export_metrics(background_tasks: BackgroundTasks):
    """Export all metrics to file"""
    try:
        def export_task():
            output_file = metrics_collector.export_metrics()
            if output_file:
                print(f"📊 Metrics exported to: {output_file}")
        
        background_tasks.add_task(export_task)
        return {"message": "Metrics export started", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting metrics: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Simple status endpoint for health checks"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime_seconds": metrics_collector.get_analytics_summary()["uptime_seconds"]
    }

# Mount static files for frontend
try:
    frontend_path = Path("frontend/admin-dashboard/dist")
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
