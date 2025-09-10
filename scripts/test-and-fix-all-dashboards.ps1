# Test and Fix All Grafana Dashboards
# Tests each dashboard and recreates any that are broken

param(
    [string]$GrafanaUrl = "http://localhost:3000",
    [string]$Username = "admin",
    [string]$Password = "admin123"
)

Write-Host "🔍 Testing All Grafana Dashboards..." -ForegroundColor Green

# Function to test dashboard
function Test-Dashboard {
    param(
        [string]$Name,
        [string]$Url
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $Name - Working" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Name - Error: $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ $Name - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to delete dashboard
function Remove-Dashboard {
    param(
        [string]$Name,
        [string]$Uid
    )
    
    try {
        $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))
        $headers = @{
            "Authorization" = "Basic $credentials"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "$GrafanaUrl/api/dashboards/uid/$Uid" -Method Delete -Headers $headers
        Write-Host "🗑️ Deleted broken dashboard: $Name" -ForegroundColor Yellow
        return $true
    }
    catch {
        Write-Host "⚠️ Could not delete $Name`: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

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

# Test all known dashboards
$dashboards = @(
    @{
        Name = "Enhanced Observability Dashboard"
        Url = "$GrafanaUrl/d/fcc04a64-1bc6-449c-b062-d55a31bcc7ba/enhanced-observability-dashboard"
        Uid = "fcc04a64-1bc6-449c-b062-d55a31bcc7ba"
    },
    @{
        Name = "LangSmith Trace Integration"
        Url = "$GrafanaUrl/d/df252788-3bf8-4ca9-aeb4-17e305c01900/langsmith-trace-integration"
        Uid = "df252788-3bf8-4ca9-aeb4-17e305c01900"
    },
    @{
        Name = "Comprehensive Observability (FINAL FIXED)"
        Url = "$GrafanaUrl/d/comprehensive-observability-final-fixed/212c19dd-12c5-5d47-aec8-0ef0c5ec6da5"
        Uid = "comprehensive-observability-final-fixed"
    },
    @{
        Name = "Vector Database Monitoring"
        Url = "$GrafanaUrl/d/dbfc728b-e8dd-4a56-b559-0d356feab788/vector-database-monitoring"
        Uid = "dbfc728b-e8dd-4a56-b559-0d356feab788"
    },
    @{
        Name = "Data Pipeline Health"
        Url = "$GrafanaUrl/d/e614609f-0dc9-4387-96fc-acd898e57f5e/data-pipeline-health"
        Uid = "e614609f-0dc9-4387-96fc-acd898e57f5e"
    },
    @{
        Name = "Performance Optimization Dashboard"
        Url = "$GrafanaUrl/d/d5d6046c-5cba-46e2-a345-0a8747bc20d3/performance-optimization-dashboard"
        Uid = "d5d6046c-5cba-46e2-a345-0a8747bc20d3"
    },
    @{
        Name = "Working Data Pipeline Dashboard - FINAL"
        Url = "$GrafanaUrl/d/e2652108-ce66-4c0e-a1cd-71ee03410fe9/working-data-pipeline-dashboard-final"
        Uid = "e2652108-ce66-4c0e-a1cd-71ee03410fe9"
    }
)

Write-Host "`n🧪 Testing Dashboard Accessibility..." -ForegroundColor Cyan

$brokenDashboards = @()
foreach ($dashboard in $dashboards) {
    if (-not (Test-Dashboard -Name $dashboard.Name -Url $dashboard.Url)) {
        $brokenDashboards += $dashboard
    }
}

if ($brokenDashboards.Count -eq 0) {
    Write-Host "`n🎉 All dashboards are working perfectly!" -ForegroundColor Green
    exit 0
}

Write-Host "`n🔧 Found $($brokenDashboards.Count) broken dashboards. Fixing..." -ForegroundColor Yellow

# Delete broken dashboards
foreach ($dashboard in $brokenDashboards) {
    Remove-Dashboard -Name $dashboard.Name -Uid $dashboard.Uid
}

# Recreate dashboards
Write-Host "`n🚀 Recreating Broken Dashboards..." -ForegroundColor Cyan

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

# Create all dashboards
Write-Host "`n🚀 Creating Enhanced Observability Dashboard..." -ForegroundColor Cyan
Create-Dashboard "Enhanced Observability Dashboard" $enhancedObservabilityDashboard

Write-Host "`n🚀 Creating LangSmith Trace Integration Dashboard..." -ForegroundColor Cyan
Create-Dashboard "LangSmith Trace Integration" $langsmithTraceDashboard

Write-Host "`n🚀 Creating Vector Database Monitoring Dashboard..." -ForegroundColor Cyan
Create-Dashboard "Vector Database Monitoring" $vectorDatabaseDashboard

Write-Host "`n🎉 Dashboard Testing and Fixing Complete!" -ForegroundColor Green
Write-Host "📊 Access your dashboards at: $GrafanaUrl" -ForegroundColor Cyan
