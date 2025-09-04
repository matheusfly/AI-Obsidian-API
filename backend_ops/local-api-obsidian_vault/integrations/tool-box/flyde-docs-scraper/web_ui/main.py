"""
FastAPI web UI for the Flyde documentation scraper.
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import structlog

from config.settings import settings
from config.logging import get_logger
from scrapers.scrapfly_scraper import ScrapflyScraper
from scrapers.playwright_scraper import PlaywrightScraper
from scrapers.scrapy_scraper import ScrapyScraper


logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Flyde Docs Scraper",
    description="Comprehensive web scraping system for Flyde documentation",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scrapers
scrapers = {
    "scrapfly": ScrapflyScraper(),
    "playwright": PlaywrightScraper(),
    "scrapy": ScrapyScraper()
}

# Store active scraping tasks
active_tasks: Dict[str, Any] = {}


# Pydantic models
class ScrapeRequest(BaseModel):
    url: str
    scraper: str = "scrapfly"
    options: Optional[Dict[str, Any]] = None


class ScrapeMultipleRequest(BaseModel):
    urls: List[str]
    scraper: str = "scrapfly"
    options: Optional[Dict[str, Any]] = None


class ScrapingStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    results: List[Dict[str, Any]]
    errors: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web UI."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flyde Docs Scraper</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select, textarea {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
            }
            button:hover {
                background-color: #0056b3;
            }
            .status {
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .success { background-color: #d4edda; color: #155724; }
            .error { background-color: #f8d7da; color: #721c24; }
            .info { background-color: #d1ecf1; color: #0c5460; }
            .results {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                margin-top: 15px;
                max-height: 400px;
                overflow-y: auto;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 4px;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #007bff;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Flyde Docs Scraper</h1>
            <p>Comprehensive web scraping system for Flyde documentation</p>
        </div>
        
        <div class="container">
            <h2>Single URL Scraping</h2>
            <form id="singleForm">
                <div class="form-group">
                    <label for="singleUrl">URL:</label>
                    <input type="url" id="singleUrl" placeholder="https://flyde.dev/docs" required>
                </div>
                <div class="form-group">
                    <label for="singleScraper">Scraper:</label>
                    <select id="singleScraper">
                        <option value="scrapfly">Scrapfly</option>
                        <option value="playwright">Playwright</option>
                        <option value="scrapy">Scrapy</option>
                    </select>
                </div>
                <button type="submit">Scrape URL</button>
            </form>
            <div id="singleStatus"></div>
            <div id="singleResults" class="results" style="display: none;"></div>
        </div>
        
        <div class="container">
            <h2>Multiple URLs Scraping</h2>
            <form id="multipleForm">
                <div class="form-group">
                    <label for="multipleUrls">URLs (one per line):</label>
                    <textarea id="multipleUrls" rows="5" placeholder="https://flyde.dev/docs&#10;https://flyde.dev/docs/introduction&#10;https://flyde.dev/docs/core-concepts"></textarea>
                </div>
                <div class="form-group">
                    <label for="multipleScraper">Scraper:</label>
                    <select id="multipleScraper">
                        <option value="scrapfly">Scrapfly</option>
                        <option value="playwright">Playwright</option>
                        <option value="scrapy">Scrapy</option>
                    </select>
                </div>
                <button type="submit">Scrape URLs</button>
            </form>
            <div id="multipleStatus"></div>
            <div id="multipleResults" class="results" style="display: none;"></div>
        </div>
        
        <div class="container">
            <h2>Scraper Statistics</h2>
            <div id="stats" class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="totalSessions">0</div>
                    <div>Total Sessions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="totalSuccesses">0</div>
                    <div>Successful Scrapes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="totalErrors">0</div>
                    <div>Errors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="successRate">0%</div>
                    <div>Success Rate</div>
                </div>
            </div>
            <button onclick="refreshStats()">Refresh Stats</button>
        </div>
        
        <script>
            async function scrapeSingle() {
                const url = document.getElementById('singleUrl').value;
                const scraper = document.getElementById('singleScraper').value;
                const statusDiv = document.getElementById('singleStatus');
                const resultsDiv = document.getElementById('singleResults');
                
                statusDiv.innerHTML = '<div class="status info">Scraping...</div>';
                resultsDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/api/scrape', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url, scraper})
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        statusDiv.innerHTML = '<div class="status success">Scraping completed successfully!</div>';
                        resultsDiv.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                        resultsDiv.style.display = 'block';
                    } else {
                        statusDiv.innerHTML = '<div class="status error">Error: ' + result.detail + '</div>';
                    }
                } catch (error) {
                    statusDiv.innerHTML = '<div class="status error">Error: ' + error.message + '</div>';
                }
                
                refreshStats();
            }
            
            async function scrapeMultiple() {
                const urlsText = document.getElementById('multipleUrls').value;
                const scraper = document.getElementById('multipleScraper').value;
                const statusDiv = document.getElementById('multipleStatus');
                const resultsDiv = document.getElementById('multipleResults');
                
                const urls = urlsText.split('\\n').filter(url => url.trim());
                
                if (urls.length === 0) {
                    statusDiv.innerHTML = '<div class="status error">Please enter at least one URL</div>';
                    return;
                }
                
                statusDiv.innerHTML = '<div class="status info">Scraping multiple URLs...</div>';
                resultsDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/api/scrape-multiple', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({urls, scraper})
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        statusDiv.innerHTML = '<div class="status success">Scraping completed successfully!</div>';
                        resultsDiv.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                        resultsDiv.style.display = 'block';
                    } else {
                        statusDiv.innerHTML = '<div class="status error">Error: ' + result.detail + '</div>';
                    }
                } catch (error) {
                    statusDiv.innerHTML = '<div class="status error">Error: ' + error.message + '</div>';
                }
                
                refreshStats();
            }
            
            async function refreshStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    
                    document.getElementById('totalSessions').textContent = stats.total_sessions;
                    document.getElementById('totalSuccesses').textContent = stats.total_successes;
                    document.getElementById('totalErrors').textContent = stats.total_errors;
                    document.getElementById('successRate').textContent = stats.success_rate + '%';
                } catch (error) {
                    console.error('Failed to refresh stats:', error);
                }
            }
            
            // Event listeners
            document.getElementById('singleForm').addEventListener('submit', function(e) {
                e.preventDefault();
                scrapeSingle();
            });
            
            document.getElementById('multipleForm').addEventListener('submit', function(e) {
                e.preventDefault();
                scrapeMultiple();
            });
            
            // Load initial stats
            refreshStats();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/scrape")
async def scrape_url(request: ScrapeRequest):
    """Scrape a single URL."""
    try:
        if request.scraper not in scrapers:
            raise HTTPException(status_code=400, detail=f"Unknown scraper: {request.scraper}")
        
        scraper = scrapers[request.scraper]
        result = await scraper.scrape_url(request.url, **(request.options or {}))
        
        return result.to_dict()
    
    except Exception as e:
        logger.error("Scraping failed", url=request.url, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape-multiple")
async def scrape_multiple_urls(request: ScrapeMultipleRequest):
    """Scrape multiple URLs."""
    try:
        if request.scraper not in scrapers:
            raise HTTPException(status_code=400, detail=f"Unknown scraper: {request.scraper}")
        
        scraper = scrapers[request.scraper]
        results = await scraper.scrape_multiple(request.urls, **(request.options or {}))
        
        return [result.to_dict() for result in results]
    
    except Exception as e:
        logger.error("Multiple scraping failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get scraping statistics."""
    total_sessions = sum(scraper.session_count for scraper in scrapers.values())
    total_successes = sum(scraper.success_count for scraper in scrapers.values())
    total_errors = sum(scraper.error_count for scraper in scrapers.values())
    
    success_rate = (total_successes / max(1, total_sessions)) * 100
    
    return {
        "total_sessions": total_sessions,
        "total_successes": total_successes,
        "total_errors": total_errors,
        "success_rate": round(success_rate, 2),
        "scrapers": {
            name: {
                "sessions": scraper.session_count,
                "successes": scraper.success_count,
                "errors": scraper.error_count,
                "success_rate": round(scraper.success_count / max(1, scraper.session_count) * 100, 2)
            }
            for name, scraper in scrapers.items()
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages here
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )