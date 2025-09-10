# Performance Optimization Dashboard Creator
# Creates a Grafana dashboard focused on performance metrics and optimization opportunities

param(
    [string]$GrafanaUrl = "http://localhost:3000",
    [string]$Username = "admin",
    [string]$Password = "admin123"
)

Write-Host "🚀 Creating Performance Optimization Dashboard..." -ForegroundColor Green

# Dashboard JSON for Performance Optimization
$dashboardJson = @"
{
  "dashboard": {
    "id": null,
    "title": "Performance Optimization Dashboard",
    "tags": ["performance", "optimization", "monitoring"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate Optimization",
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
        "title": "Memory Usage Optimization",
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
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Cache Hit Rate",
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
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Response Time Percentiles",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Response Time"
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
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "Optimization Opportunities",
        "type": "table",
        "targets": [
          {
            "expr": "topk(5, rate(http_requests_total[5m]))",
            "legendFormat": "Top Endpoints by Request Rate"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
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

# Create the dashboard
try {
    # Use basic authentication instead of API key
    $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))
    $headers = @{
        "Authorization" = "Basic $credentials"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "$GrafanaUrl/api/dashboards/db" -Method Post -Body $dashboardJson -Headers $headers
    
    Write-Host "✅ Performance Optimization Dashboard created successfully!" -ForegroundColor Green
    Write-Host "📊 Dashboard URL: $GrafanaUrl/d/$($response.id)" -ForegroundColor Cyan
}
catch {
    Write-Host "❌ Error creating dashboard: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎯 Performance Optimization Dashboard Setup Complete!" -ForegroundColor Green
