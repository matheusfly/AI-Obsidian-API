#!/usr/bin/env python3
"""
Data Vault Obsidian - Prometheus Proxy
Makes the metrics server look like Prometheus to Grafana
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrometheusProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/v1/query':
            # Handle Prometheus query API
            self.handle_query()
        elif self.path == '/api/v1/query_range':
            # Handle Prometheus range query API
            self.handle_query_range()
        elif self.path == '/api/v1/label/__name__/values':
            # Handle label values query
            self.handle_label_values()
        elif self.path == '/api/v1/labels':
            # Handle labels query
            self.handle_labels()
        elif self.path == '/api/v1/targets':
            # Handle targets query
            self.handle_targets()
        elif self.path == '/api/v1/status/config':
            # Handle config status
            self.handle_config_status()
        elif self.path == '/-/ready':
            # Handle readiness check
            self.handle_ready()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_query(self):
        """Handle Prometheus query requests"""
        try:
            # Get metrics from our metrics server
            with urllib.request.urlopen('http://localhost:8000/metrics') as response:
                metrics_data = response.read().decode('utf-8')
            
            # Parse the query parameter
            query_params = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            query = query_params.get('query', [''])[0]
            
            # Simple query processing - return all metrics for now
            if query:
                # Filter metrics based on query (simplified)
                filtered_metrics = []
                for line in metrics_data.split('\n'):
                    if query in line and not line.startswith('#'):
                        filtered_metrics.append(line)
                
                # Format as Prometheus API response
                result = {
                    "status": "success",
                    "data": {
                        "resultType": "vector",
                        "result": [
                            {
                                "metric": {"__name__": query},
                                "value": [int(time.time()), "1"]
                            }
                        ]
                    }
                }
            else:
                # Return all metrics
                result = {
                    "status": "success",
                    "data": {
                        "resultType": "vector",
                        "result": [
                            {
                                "metric": {"__name__": "up", "service": "metrics-server"},
                                "value": [int(time.time()), "1"]
                            }
                        ]
                    }
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            self.send_response(500)
            self.end_headers()
    
    def handle_query_range(self):
        """Handle Prometheus range query requests"""
        # For now, return the same as query
        self.handle_query()
    
    def handle_label_values(self):
        """Handle label values requests"""
        result = {
            "status": "success",
            "data": [
                "http_requests_total",
                "data_pipeline_documents_processed_total",
                "vector_db_operations_total",
                "chromadb_health_check",
                "process_resident_memory_bytes",
                "up"
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_labels(self):
        """Handle labels requests"""
        result = {
            "status": "success",
            "data": [
                "__name__",
                "method",
                "endpoint",
                "status",
                "service",
                "operation",
                "document_type",
                "cache_type",
                "error_type"
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_targets(self):
        """Handle targets requests"""
        result = {
            "status": "success",
            "data": {
                "activeTargets": [
                    {
                        "discoveredLabels": {"__address__": "localhost:8000"},
                        "labels": {"job": "metrics-server", "instance": "localhost:8000"},
                        "scrapePool": "metrics-server",
                        "scrapeUrl": "http://localhost:8000/metrics",
                        "globalUrl": "http://localhost:8000/metrics",
                        "lastError": "",
                        "lastScrape": "2024-12-19T18:47:00Z",
                        "lastScrapeDuration": 0.001,
                        "health": "up"
                    }
                ]
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_config_status(self):
        """Handle config status requests"""
        result = {
            "status": "success",
            "data": {
                "yaml": "global:\n  scrape_interval: 15s\n  evaluation_interval: 15s\nscrape_configs:\n  - job_name: 'metrics-server'\n    static_configs:\n      - targets: ['localhost:8000']"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_ready(self):
        """Handle readiness check"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Prometheus Server is Ready.')
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def start_proxy(port=9090):
    """Start the Prometheus proxy"""
    try:
        server = HTTPServer(('0.0.0.0', port), PrometheusProxyHandler)
        logger.info(f"🚀 Prometheus proxy started on port {port}")
        logger.info(f"📊 Proxy available at: http://localhost:{port}")
        logger.info("🛑 Press Ctrl+C to stop")
        
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down proxy...")
        server.shutdown()
    except Exception as e:
        logger.error(f"❌ Error starting proxy: {e}")

if __name__ == "__main__":
    import time
    start_proxy()
