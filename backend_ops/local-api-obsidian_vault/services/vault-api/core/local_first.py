"""
Local-First Architecture Core Module
Ensures data sovereignty and offline-first operations
"""
import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import aiofiles
from dataclasses import dataclass, asdict

@dataclass
class LocalOperation:
    id: str
    operation: str
    data: Dict[str, Any]
    timestamp: datetime
    status: str = "pending"
    retry_count: int = 0

class LocalFirstManager:
    def __init__(self, vault_path: str, cache_dir: str = "./cache"):
        self.vault_path = Path(vault_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "local_operations.db"
        self.init_db()
        
    def init_db(self):
        """Initialize local SQLite database for operations tracking"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id TEXT PRIMARY KEY,
                operation TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                path TEXT PRIMARY KEY,
                hash TEXT NOT NULL,
                size INTEGER NOT NULL,
                modified TEXT NOT NULL,
                synced TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    async def queue_operation(self, operation: str, data: Dict[str, Any]) -> str:
        """Queue operation for local-first processing"""
        op_id = hashlib.md5(f"{operation}{datetime.now().isoformat()}".encode()).hexdigest()
        local_op = LocalOperation(
            id=op_id,
            operation=operation,
            data=data,
            timestamp=datetime.now()
        )
        
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO operations VALUES (?, ?, ?, ?, ?, ?)",
            (local_op.id, local_op.operation, json.dumps(local_op.data), 
             local_op.timestamp.isoformat(), local_op.status, local_op.retry_count)
        )
        conn.commit()
        conn.close()
        
        # Execute immediately if possible
        await self.execute_operation(local_op)
        return op_id
    
    async def execute_operation(self, operation: LocalOperation):
        """Execute local operation with fallback handling"""
        try:
            if operation.operation == "create_note":
                await self._create_note_local(operation.data)
            elif operation.operation == "update_note":
                await self._update_note_local(operation.data)
            elif operation.operation == "delete_note":
                await self._delete_note_local(operation.data)
            
            self._mark_operation_complete(operation.id)
        except Exception as e:
            self._mark_operation_failed(operation.id, str(e))
    
    async def _create_note_local(self, data: Dict[str, Any]):
        """Create note in local vault"""
        file_path = self.vault_path / data["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(data["content"])
        
        await self._update_file_metadata(data["path"])
    
    async def _update_note_local(self, data: Dict[str, Any]):
        """Update note in local vault"""
        file_path = self.vault_path / data["path"]
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(data["content"])
        
        await self._update_file_metadata(data["path"])
    
    async def _delete_note_local(self, data: Dict[str, Any]):
        """Delete note from local vault"""
        file_path = self.vault_path / data["path"]
        if file_path.exists():
            file_path.unlink()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM file_metadata WHERE path = ?", (data["path"],))
        conn.commit()
        conn.close()
    
    async def _update_file_metadata(self, path: str):
        """Update file metadata in local database"""
        file_path = self.vault_path / path
        if not file_path.exists():
            return
        
        stat = file_path.stat()
        content_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO file_metadata 
            VALUES (?, ?, ?, ?, ?)
        """, (path, content_hash, stat.st_size, 
              datetime.fromtimestamp(stat.st_mtime).isoformat(), None))
        conn.commit()
        conn.close()
    
    def _mark_operation_complete(self, op_id: str):
        """Mark operation as completed"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE operations SET status = 'completed' WHERE id = ?", 
            (op_id,)
        )
        conn.commit()
        conn.close()
    
    def _mark_operation_failed(self, op_id: str, error: str):
        """Mark operation as failed"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE operations SET status = 'failed', retry_count = retry_count + 1 WHERE id = ?", 
            (op_id,)
        )
        conn.commit()
        conn.close()
    
    async def get_pending_operations(self) -> List[LocalOperation]:
        """Get all pending operations for retry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM operations WHERE status = 'pending' OR status = 'failed'"
        )
        operations = []
        for row in cursor.fetchall():
            operations.append(LocalOperation(
                id=row[0],
                operation=row[1],
                data=json.loads(row[2]),
                timestamp=datetime.fromisoformat(row[3]),
                status=row[4],
                retry_count=row[5]
            ))
        conn.close()
        return operations
    
    async def sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        conn = sqlite3.connect(self.db_path)
        
        # Count operations by status
        cursor = conn.execute(
            "SELECT status, COUNT(*) FROM operations GROUP BY status"
        )
        op_counts = dict(cursor.fetchall())
        
        # Count files
        cursor = conn.execute("SELECT COUNT(*) FROM file_metadata")
        file_count = cursor.fetchone()[0]
        
        # Count unsynced files
        cursor = conn.execute(
            "SELECT COUNT(*) FROM file_metadata WHERE synced IS NULL"
        )
        unsynced_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "operations": op_counts,
            "files": {
                "total": file_count,
                "unsynced": unsynced_count,
                "synced": file_count - unsynced_count
            },
            "vault_path": str(self.vault_path),
            "last_check": datetime.now().isoformat()
        }