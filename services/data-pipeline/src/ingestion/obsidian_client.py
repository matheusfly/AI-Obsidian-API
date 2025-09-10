"""
Obsidian Local REST API Client for data ingestion
"""
import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ObsidianAPIClient:
    """Client for interacting with Obsidian Local REST API"""
    
    def __init__(self, api_key: str, host: str = "127.0.0.1", port: int = 27123):
        self.api_key = api_key
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
        self._connection_tested = False
    
    async def test_connection(self) -> bool:
        """Test connection to Obsidian API"""
        try:
            response = await self.client.get(f"{self.base_url}/vault/")
            if response.status_code == 200:
                self._connection_tested = True
                logger.info("Successfully connected to Obsidian API")
                return True
            else:
                logger.error(f"Failed to connect to Obsidian API: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error testing Obsidian API connection: {e}")
            return False
    
    async def list_vault_files(self, recursive: bool = True) -> List[Dict[str, Any]]:
        """List all files in the vault"""
        if not self._connection_tested:
            await self.test_connection()
        
        try:
            response = await self.client.get(f"{self.base_url}/vault/")
            response.raise_for_status()
            files = response.json()
            
            # Filter for markdown files
            markdown_files = [
                file for file in files 
                if file.get('path', '').endswith('.md')
            ]
            
            logger.info(f"Found {len(markdown_files)} markdown files in vault")
            return markdown_files
            
        except Exception as e:
            logger.error(f"Error listing vault files: {e}")
            raise
    
    async def get_file_content(self, path: str) -> Dict[str, Any]:
        """Get file content and metadata"""
        try:
            response = await self.client.get(f"{self.base_url}/vault/{path}")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting file content for {path}: {e}")
            raise
    
    async def get_file_metadata(self, path: str) -> Dict[str, Any]:
        """Get file metadata"""
        try:
            response = await self.client.get(f"{self.base_url}/vault/{path}/metadata")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting file metadata for {path}: {e}")
            raise
    
    async def search_vault(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search vault content"""
        try:
            response = await self.client.post(
                f"{self.base_url}/vault/search",
                json={"query": query, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error searching vault: {e}")
            raise
    
    async def get_vault_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        try:
            response = await self.client.get(f"{self.base_url}/vault/stats")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting vault stats: {e}")
            raise
    
    async def batch_get_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Get multiple files in batch"""
        results = []
        
        # Process in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            
            # Create tasks for concurrent requests
            tasks = [self.get_file_content(path) for path in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error getting file {batch[j]}: {result}")
                    results.append({
                        "path": batch[j],
                        "error": str(result),
                        "content": None
                    })
                else:
                    results.append(result)
            
            # Small delay between batches
            await asyncio.sleep(0.1)
        
        return results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'client'):
            asyncio.create_task(self.client.aclose())


class ObsidianVaultScanner:
    """Scanner for discovering and processing Obsidian vault content"""
    
    def __init__(self, api_client: ObsidianAPIClient):
        self.api_client = api_client
        self.scanned_files = set()
        self.file_hashes = {}
    
    async def scan_vault(self) -> Dict[str, Any]:
        """Scan entire vault and return summary"""
        logger.info("Starting vault scan...")
        
        # Get vault stats
        stats = await self.api_client.get_vault_stats()
        
        # List all files
        files = await self.api_client.list_vault_files()
        
        # Filter markdown files
        markdown_files = [f for f in files if f.get('path', '').endswith('.md')]
        
        scan_summary = {
            "total_files": len(files),
            "markdown_files": len(markdown_files),
            "vault_stats": stats,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "files": markdown_files
        }
        
        logger.info(f"Vault scan complete: {len(markdown_files)} markdown files found")
        return scan_summary
    
    async def get_file_changes(self, since_timestamp: Optional[datetime] = None) -> List[str]:
        """Get list of files that have changed since timestamp"""
        # This would require file watching or metadata comparison
        # For now, return all files (incremental updates can be added later)
        files = await self.api_client.list_vault_files()
        return [f['path'] for f in files if f.get('path', '').endswith('.md')]
    
    def calculate_file_hash(self, content: str) -> str:
        """Calculate hash for file content"""
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def has_file_changed(self, path: str, content: str) -> bool:
        """Check if file has changed since last scan"""
        current_hash = self.calculate_file_hash(content)
        previous_hash = self.file_hashes.get(path)
        
        if previous_hash != current_hash:
            self.file_hashes[path] = current_hash
            return True
        
        return False
