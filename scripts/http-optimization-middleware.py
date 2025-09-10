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
