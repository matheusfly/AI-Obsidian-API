#!/usr/bin/env python3
"""
File Watcher Service for Obsidian Vault
Monitors file changes and triggers webhooks
"""

import os
import time
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import FastAPI, HTTPException
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
VAULT_PATH = os.getenv('VAULT_PATH', '/vault')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://n8n:5678/webhook/file-change')
API_KEY = os.getenv('API_KEY', 'obsidian_secure_key_2024')
PORT = int(os.getenv('PORT', 8000))

# FastAPI app
app = FastAPI(title="File Watcher Service", version="1.0.0")

class VaultFileHandler(FileSystemEventHandler):
    """Handle file system events in the Obsidian vault"""
    
    def __init__(self):
        self.last_events = {}
        self.debounce_time = 2.0  # seconds
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._handle_file_event('modified', event.src_path)
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._handle_file_event('created', event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._handle_file_event('deleted', event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory and event.dest_path.endswith('.md'):
            self._handle_file_event('moved', event.dest_path, old_path=event.src_path)
    
    def _handle_file_event(self, event_type: str, file_path: str, old_path: str = None):
        """Handle file events with debouncing"""
        current_time = time.time()
        event_key = f"{event_type}:{file_path}"
        
        # Debounce events
        if event_key in self.last_events:
            if current_time - self.last_events[event_key] < self.debounce_time:
                return
        
        self.last_events[event_key] = current_time
        
        # Prepare event data
        event_data = {
            'event_type': event_type,
            'file_path': file_path,
            'relative_path': os.path.relpath(file_path, VAULT_PATH),
            'timestamp': current_time,
            'vault_path': VAULT_PATH
        }
        
        if old_path:
            event_data['old_path'] = old_path
            event_data['old_relative_path'] = os.path.relpath(old_path, VAULT_PATH)
        
        # Get file stats if file exists
        if os.path.exists(file_path):
            try:
                stat = os.stat(file_path)
                event_data['file_size'] = stat.st_size
                event_data['modified_time'] = stat.st_mtime
            except OSError:
                pass
        
        # Send webhook
        self._send_webhook(event_data)
    
    def _send_webhook(self, event_data: Dict[str, Any]):
        """Send webhook notification"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}',
                'User-Agent': 'Obsidian-FileWatcher/1.0.0'
            }
            
            response = requests.post(
                WEBHOOK_URL,
                json=event_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully for {event_data['event_type']}: {event_data['relative_path']}")
            else:
                logger.warning(f"Webhook failed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook: {e}")

# Global observer
observer = None
file_handler = None

@app.on_event("startup")
async def startup_event():
    """Start the file watcher on startup"""
    global observer, file_handler
    
    logger.info(f"Starting file watcher for vault: {VAULT_PATH}")
    logger.info(f"Webhook URL: {WEBHOOK_URL}")
    
    # Check if vault path exists
    if not os.path.exists(VAULT_PATH):
        logger.error(f"Vault path does not exist: {VAULT_PATH}")
        return
    
    # Initialize file handler and observer
    file_handler = VaultFileHandler()
    observer = Observer()
    observer.schedule(file_handler, VAULT_PATH, recursive=True)
    
    # Start watching
    observer.start()
    logger.info("File watcher started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the file watcher on shutdown"""
    global observer
    
    if observer:
        observer.stop()
        observer.join()
        logger.info("File watcher stopped")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "file-watcher",
        "vault_path": VAULT_PATH,
        "webhook_url": WEBHOOK_URL,
        "watching": observer.is_alive() if observer else False
    }

@app.get("/status")
async def get_status():
    """Get detailed status"""
    return {
        "status": "running",
        "service": "file-watcher",
        "vault_path": VAULT_PATH,
        "webhook_url": WEBHOOK_URL,
        "observer_running": observer.is_alive() if observer else False,
        "total_events": len(file_handler.last_events) if file_handler else 0
    }

@app.post("/restart")
async def restart_watcher():
    """Restart the file watcher"""
    global observer, file_handler
    
    try:
        # Stop current observer
        if observer:
            observer.stop()
            observer.join()
        
        # Start new observer
        file_handler = VaultFileHandler()
        observer = Observer()
        observer.schedule(file_handler, VAULT_PATH, recursive=True)
        observer.start()
        
        logger.info("File watcher restarted successfully")
        return {"status": "restarted", "message": "File watcher restarted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to restart file watcher: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting File Watcher Service...")
    uvicorn.run(
        "file_watcher:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )
