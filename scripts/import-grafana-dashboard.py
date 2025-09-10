#!/usr/bin/env python3
"""
Import dashboard into Grafana
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin123"

def get_auth_token():
    """Get Grafana authentication token"""
    try:
        response = requests.post(f"{GRAFANA_URL}/api/auth/keys", 
                               json={"name": "dashboard-import", "role": "Admin"},
                               auth=(GRAFANA_USER, GRAFANA_PASSWORD))
        
        if response.status_code == 200:
            return response.json()["key"]
        else:
            logger.error(f"Failed to get auth token: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting auth token: {e}")
        return None

def create_datasource():
    """Create Prometheus datasource"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    datasource_config = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://localhost:9090",
        "access": "proxy",
        "isDefault": True
    }
    
    try:
        response = requests.post(f"{GRAFANA_URL}/api/datasources", 
                               json=datasource_config, 
                               headers=headers)
        
        if response.status_code == 200:
            logger.info("✅ Prometheus datasource created")
            return True
        else:
            logger.info(f"Datasource may already exist: {response.status_code}")
            return True
    except Exception as e:
        logger.error(f"Error creating datasource: {e}")
        return False

def create_dashboard():
    """Create comprehensive dashboard"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    dashboard_config = {
        "dashboard": {
            "id": None,
            "title": "Data Vault Obsidian - Comprehensive Monitoring",
            "tags": ["data-vault", "obsidian", "monitoring"],
            "style": "dark",
            "timezone": "browser",
            "refresh": "5s",
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "System Overview",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "up",
                            "legendFormat": "Services Up"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "steps": [
                                    {"color": "red", "value": 0},
                                    {"color": "green", "value": 1}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "HTTP Requests",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "http_requests_total",
                            "legendFormat": "{{method}} {{endpoint}} {{status}}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Data Pipeline Processing",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "data_pipeline_documents_processed_total",
                            "legendFormat": "{{status}}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                },
                {
                    "id": 4,
                    "title": "Vector Database Operations",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "vector_db_operations_total",
                            "legendFormat": "{{operation}}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                },
                {
                    "id": 5,
                    "title": "ChromaDB Health",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "chromadb_health_check",
                            "legendFormat": "ChromaDB Status"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "steps": [
                                    {"color": "red", "value": 0},
                                    {"color": "green", "value": 1}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 8, "x": 0, "y": 16}
                },
                {
                    "id": 6,
                    "title": "Memory Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "process_resident_memory_bytes",
                            "legendFormat": "Memory Usage"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 8, "x": 8, "y": 16}
                },
                {
                    "id": 7,
                    "title": "CPU Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "process_cpu_seconds_total",
                            "legendFormat": "CPU Usage"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 8, "x": 16, "y": 16}
                },
                {
                    "id": 8,
                    "title": "Cache Performance",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "cache_hits_total",
                            "legendFormat": "Hits {{cache_type}}"
                        },
                        {
                            "expr": "cache_misses_total",
                            "legendFormat": "Misses {{cache_type}}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 24}
                },
                {
                    "id": 9,
                    "title": "Active Connections",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "http_connections_active",
                            "legendFormat": "Active Connections"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 24}
                }
            ]
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(f"{GRAFANA_URL}/api/dashboards/db", 
                               json=dashboard_config, 
                               headers=headers)
        
        if response.status_code == 200:
            logger.info("✅ Dashboard created successfully")
            return True
        else:
            logger.error(f"Failed to create dashboard: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        return False

def main():
    """Main function"""
    logger.info("🔧 Setting up Grafana dashboard...")
    
    # Wait for Grafana to be ready
    max_retries = 30
    retries = 0
    
    while retries < max_retries:
        try:
            response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Grafana is ready")
                break
        except:
            pass
        
        retries += 1
        time.sleep(2)
    
    if retries >= max_retries:
        logger.error("❌ Grafana is not ready")
        return False
    
    # Create datasource
    if not create_datasource():
        logger.error("❌ Failed to create datasource")
        return False
    
    # Create dashboard
    if not create_dashboard():
        logger.error("❌ Failed to create dashboard")
        return False
    
    logger.info("🎉 Dashboard setup complete!")
    logger.info("📊 Access Grafana at: http://localhost:3000")
    logger.info("👤 Login: admin / admin123")
    
    return True

if __name__ == "__main__":
    main()
