import sqlite3
from api_gateway.config import settings
from typing import List, Dict, Any, Optional

class GraphDatabase:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.graph_db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with the required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes(
                id TEXT PRIMARY KEY,
                path TEXT,
                heading TEXT,
                hash TEXT,
                last_modified TIMESTAMP
            )
        """)
        
        # Create edges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges(
                id TEXT PRIMARY KEY,
                src TEXT,
                dst TEXT,
                type TEXT,
                FOREIGN KEY(src) REFERENCES nodes(id),
                FOREIGN KEY(dst) REFERENCES nodes(id)
            )
        """)
        
        # Create node_metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_metadata(
                node_id TEXT,
                key TEXT,
                value TEXT,
                FOREIGN KEY(node_id) REFERENCES nodes(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_node(self, node_id: str, path: str, heading: str, hash: str, last_modified: str):
        """Add a node to the graph database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO nodes (id, path, heading, hash, last_modified)
            VALUES (?, ?, ?, ?, ?)
        """, (node_id, path, heading, hash, last_modified))
        
        conn.commit()
        conn.close()
    
    def add_edge(self, edge_id: str, src: str, dst: str, edge_type: str):
        """Add an edge to the graph database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO edges (id, src, dst, type)
            VALUES (?, ?, ?, ?)
        """, (edge_id, src, dst, edge_type))
        
        conn.commit()
        conn.close()
    
    def add_node_metadata(self, node_id: str, key: str, value: str):
        """Add metadata to a node"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO node_metadata (node_id, key, value)
            VALUES (?, ?, ?)
        """, (node_id, key, value))
        
        conn.commit()
        conn.close()
    
    def get_related_nodes(self, node_id: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Find nodes related to a specific node"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT n.path, n.heading FROM edges e
            JOIN nodes n ON (e.dst = n.id OR e.src = n.id)
            WHERE (e.src = ? OR e.dst = ?) AND n.id != ?
            LIMIT ?
        """, (node_id, node_id, node_id, max_results))
        
        related = cursor.fetchall()
        conn.close()
        
        return [{"path": row[0], "heading": row[1]} for row in related]