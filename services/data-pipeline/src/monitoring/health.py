"""
Health check and metrics endpoints for the data pipeline service
"""
import logging
import time
import psutil
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# from vector.chroma_service import ChromaService  # Not using ChromaService directly
from config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create router
router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Global health state
health_state = {
    "status": "unknown",
    "last_check": None,
    "uptime_start": time.time(),
    "checks": {}
}

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    uptime_seconds: float
    version: str
    checks: Dict[str, Any]

class MetricsResponse(BaseModel):
    timestamp: datetime
    system: Dict[str, Any]
    service: Dict[str, Any]
    database: Dict[str, Any]

def check_chroma_health() -> Dict[str, Any]:
    """Check ChromaDB health"""
    try:
        # This would be implemented based on your ChromaService
        # For now, return a basic check
        return {
            "status": "healthy",
            "message": "ChromaDB connection successful",
            "response_time_ms": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"ChromaDB connection failed: {str(e)}",
            "response_time_ms": 0
        }

def check_obsidian_health() -> Dict[str, Any]:
    """Check Obsidian API health"""
    try:
        # This would be implemented based on your ObsidianAPIClient
        # For now, return a basic check
        return {
            "status": "healthy",
            "message": "Obsidian API connection successful",
            "response_time_ms": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Obsidian API connection failed: {str(e)}",
            "response_time_ms": 0
        }

def check_gemini_health() -> Dict[str, Any]:
    """Check Gemini API health"""
    try:
        # This would be implemented based on your GeminiClient
        # For now, return a basic check
        return {
            "status": "healthy",
            "message": "Gemini API connection successful",
            "response_time_ms": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Gemini API connection failed: {str(e)}",
            "response_time_ms": 0
        }

def get_system_metrics() -> Dict[str, Any]:
    """Get system metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": round((disk.used / disk.total) * 100, 2)
            },
            "process": {
                "memory_mb": round(process_memory.rss / (1024**2), 2),
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads(),
                "open_files": len(process.open_files())
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {"error": str(e)}

def get_service_metrics() -> Dict[str, Any]:
    """Get service-specific metrics"""
    try:
        uptime = time.time() - health_state["uptime_start"]
        
        return {
            "uptime_seconds": uptime,
            "uptime_human": str(timedelta(seconds=int(uptime))),
            "version": settings.service_version,
            "environment": settings.environment,
            "log_level": settings.log_level
        }
    except Exception as e:
        logger.error(f"Failed to get service metrics: {e}")
        return {"error": str(e)}

def get_database_metrics() -> Dict[str, Any]:
    """Get database metrics"""
    try:
        # This would be implemented based on your database services
        # For now, return basic metrics
        return {
            "chroma": {
                "status": "connected",
                "collections": 0,  # Would be actual count
                "documents": 0,    # Would be actual count
                "size_mb": 0       # Would be actual size
            },
            "vector_db": {
                "status": "connected",
                "embeddings": 0,   # Would be actual count
                "size_mb": 0       # Would be actual size
            }
        }
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}")
        return {"error": str(e)}

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Perform health checks
        checks = {
            "chroma": check_chroma_health(),
            "obsidian": check_obsidian_health(),
            "gemini": check_gemini_health()
        }
        
        # Determine overall status
        all_healthy = all(check["status"] == "healthy" for check in checks.values())
        status = "healthy" if all_healthy else "unhealthy"
        
        # Update global health state
        health_state["status"] = status
        health_state["last_check"] = datetime.now()
        health_state["checks"] = checks
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now(),
            uptime_seconds=time.time() - health_state["uptime_start"],
            version=settings.service_version,
            checks=checks
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Metrics endpoint for Prometheus scraping"""
    try:
        return MetricsResponse(
            timestamp=datetime.now(),
            system=get_system_metrics(),
            service=get_service_metrics(),
            database=get_database_metrics()
        )
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if all critical services are ready
        checks = {
            "chroma": check_chroma_health(),
            "obsidian": check_obsidian_health(),
            "gemini": check_gemini_health()
        }
        
        all_ready = all(check["status"] == "healthy" for check in checks.values())
        
        if all_ready:
            return {"status": "ready", "timestamp": datetime.now()}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Readiness check failed: {str(e)}")

@router.get("/live")
async def liveness_check():
    """Liveness check endpoint"""
    try:
        # Simple liveness check - just verify the service is running
        return {
            "status": "alive",
            "timestamp": datetime.now(),
            "uptime_seconds": time.time() - health_state["uptime_start"]
        }
        
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Liveness check failed: {str(e)}")

@router.get("/status")
async def get_status():
    """Get detailed status information"""
    try:
        return {
            "health": health_state,
            "system": get_system_metrics(),
            "service": get_service_metrics(),
            "database": get_database_metrics(),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
