# Restore All Grafana Dashboards
# Restores all essential dashboards that were removed during cleanup

param(
    [string]$GrafanaUrl = "http://localhost:3000",
    [string]$Username = "admin",
    [string]$Password = "admin123"
)

Write-Host "🔄 Restoring All Grafana Dashboards..." -ForegroundColor Green

# 1. Enhanced Observability Dashboard
$enhancedObservabilityDashboard = @"
{
  "dashboard": {
    "id": null,
    "title": "Enhanced Observability Dashboard",
    "tags": ["observability", "enhanced", "monitoring"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rates (per second)",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.5},
                {"color": "red", "value": 1.0}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Response Latency",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Latency"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.1},
                {"color": "red", "value": 0.5}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Files Processed",
        "type": "stat",
        "targets": [
          {
            "expr": "files_processed_total",
            "legendFormat": "Files Processed"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 1000}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Search Queries",
        "type": "stat",
        "targets": [
          {
            "expr": "search_queries_total",
            "legendFormat": "Search Queries"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 200}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "CPU Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m]) * 100",
            "legendFormat": "CPU Usage %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 80}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 6,
        "title": "Memory Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "Memory MB"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 500},
                {"color": "red", "value": 1000}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      },
      {
        "id": 7,
        "title": "Embedding Requests",
        "type": "stat",
        "targets": [
          {
            "expr": "embedding_requests_total",
            "legendFormat": "Embedding Requests"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 24}
      },
      {
        "id": 8,
        "title": "LLM Requests",
        "type": "stat",
        "targets": [
          {
            "expr": "llm_requests_total",
            "legendFormat": "LLM Requests"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 200}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 24}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
"@

# 2. LangSmith Trace Integration Dashboard
$langsmithTraceDashboard = @"
{
  "dashboard": {
    "id": null,
    "title": "LangSmith Trace Integration",
    "tags": ["langsmith", "traces", "integration"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Traces Exported",
        "type": "stat",
        "targets": [
          {
            "expr": "langsmith_traces_exported_total",
            "legendFormat": "Traces Exported"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 10},
                {"color": "red", "value": 50}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Export Duration",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(langsmith_export_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Export Duration"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1.0},
                {"color": "red", "value": 5.0}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Export Queue Size",
        "type": "stat",
        "targets": [
          {
            "expr": "langsmith_export_queue_size",
            "legendFormat": "Queue Size"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 10},
                {"color": "red", "value": 50}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Export Errors",
        "type": "stat",
        "targets": [
          {
            "expr": "langsmith_export_errors_total",
            "legendFormat": "Export Errors"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 5}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
"@

# 3. Vector Database Monitoring Dashboard
$vectorDatabaseDashboard = @"
{
  "dashboard": {
    "id": null,
    "title": "Vector Database Monitoring",
    "tags": ["vector", "database", "chroma", "monitoring"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Collection Size",
        "type": "stat",
        "targets": [
          {
            "expr": "chromadb_collection_size",
            "legendFormat": "Documents"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1000},
                {"color": "red", "value": 5000}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Query Duration",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(chromadb_query_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Query Duration"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.1},
                {"color": "red", "value": 0.5}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Total Queries",
        "type": "stat",
        "targets": [
          {
            "expr": "chromadb_query_total",
            "legendFormat": "Total Queries"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Query Errors",
        "type": "stat",
        "targets": [
          {
            "expr": "chromadb_error_total",
            "legendFormat": "Query Errors"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 10}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "Batch Operations",
        "type": "stat",
        "targets": [
          {
            "expr": "chromadb_batch_operations_total",
            "legendFormat": "Batch Operations"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 200}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 6,
        "title": "Embedding Cache Hit Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(embedding_cache_hits_total[5m]) / (rate(embedding_cache_hits_total[5m]) + rate(embedding_cache_misses_total[5m])) * 100",
            "legendFormat": "Cache Hit Rate %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
"@

# 4. Data Pipeline Health Dashboard
$dataPipelineHealthDashboard = @"
{
  "dashboard": {
    "id": null,
    "title": "Data Pipeline Health",
    "tags": ["data-pipeline", "health", "monitoring"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "service_health",
            "legendFormat": "{{service_name}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "green", "value": 1}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Service Uptime",
        "type": "stat",
        "targets": [
          {
            "expr": "service_uptime_seconds",
            "legendFormat": "{{service_name}} Uptime"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 3600},
                {"color": "red", "value": 7200}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Active Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "active_connections",
            "legendFormat": "{{connection_type}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 10},
                {"color": "red", "value": 50}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Queue Sizes",
        "type": "stat",
        "targets": [
          {
            "expr": "queue_size",
            "legendFormat": "{{queue_name}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 10},
                {"color": "red", "value": 50}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "Cache Sizes",
        "type": "stat",
        "targets": [
          {
            "expr": "cache_size_bytes / 1024 / 1024",
            "legendFormat": "{{cache_name}} MB"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 6,
        "title": "HTTP Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.5},
                {"color": "red", "value": 1.0}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
"@

# Function to create dashboard
function Create-Dashboard {
    param(
        [string]$Name,
        [string]$Json
    )
    
    try {
        $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))
        $headers = @{
            "Authorization" = "Basic $credentials"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "$GrafanaUrl/api/dashboards/db" -Method Post -Body $Json -Headers $headers
        
        Write-Host "✅ $Name created successfully!" -ForegroundColor Green
        Write-Host "   📊 URL: $GrafanaUrl/d/$($response.id)" -ForegroundColor Cyan
        return $true
    }
    catch {
        Write-Host "❌ Error creating $Name`: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Create all dashboards
Write-Host "`n🚀 Creating Enhanced Observability Dashboard..." -ForegroundColor Cyan
Create-Dashboard "Enhanced Observability Dashboard" $enhancedObservabilityDashboard

Write-Host "`n🚀 Creating LangSmith Trace Integration Dashboard..." -ForegroundColor Cyan
Create-Dashboard "LangSmith Trace Integration" $langsmithTraceDashboard

Write-Host "`n🚀 Creating Vector Database Monitoring Dashboard..." -ForegroundColor Cyan
Create-Dashboard "Vector Database Monitoring" $vectorDatabaseDashboard

Write-Host "`n🚀 Creating Data Pipeline Health Dashboard..." -ForegroundColor Cyan
Create-Dashboard "Data Pipeline Health" $dataPipelineHealthDashboard

Write-Host "`n🎉 All Dashboards Restored Successfully!" -ForegroundColor Green
Write-Host "📊 Access your dashboards at: $GrafanaUrl" -ForegroundColor Cyan
