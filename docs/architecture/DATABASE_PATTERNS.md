# 🗄️ **DATABASE PATTERNS & TECHNIQUES**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **PRODUCTION-READY DATABASE ARCHITECTURE**

---

## 🎯 **DATABASE ARCHITECTURE PHILOSOPHY**

The Data Vault Obsidian database architecture follows **Polyglot Persistence** principles with **Clean Architecture** patterns, supporting multiple database types optimized for specific use cases while maintaining data consistency and performance.

### **Core Database Principles**

- **Polyglot Persistence** - Right database for right use case
- **ACID Compliance** - Data consistency and reliability
- **Horizontal Scaling** - Distributed database architecture
- **Data Modeling** - Domain-driven database design
- **Performance Optimization** - Query optimization and indexing
- **Data Integrity** - Constraints and validation
- **Backup & Recovery** - Data protection and disaster recovery

---

## 🏗️ **DATABASE ARCHITECTURE PATTERNS**

### **1. Repository Pattern**

#### **Generic Repository Implementation**
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    def __init__(self, session: Session, model_class: type):
        self.session = session
        self.model_class = model_class
    
    def create(self, entity: T) -> T:
        """Create a new entity"""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        return self.session.query(self.model_class)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def update(self, entity: T) -> T:
        """Update existing entity"""
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def delete(self, entity_id: Any) -> bool:
        """Delete entity by ID"""
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[T]:
        """Find entities by criteria"""
        query = self.session.query(self.model_class)
        
        for field, value in criteria.items():
            if hasattr(self.model_class, field):
                if isinstance(value, list):
                    query = query.filter(getattr(self.model_class, field).in_(value))
                else:
                    query = query.filter(getattr(self.model_class, field) == value)
        
        return query.all()
    
    def count(self, criteria: Dict[str, Any] = None) -> int:
        """Count entities matching criteria"""
        query = self.session.query(self.model_class)
        
        if criteria:
            for field, value in criteria.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)
        
        return query.count()

class NoteRepository(BaseRepository[Note]):
    def __init__(self, session: Session):
        super().__init__(session, Note)
    
    def find_by_title(self, title: str) -> List[Note]:
        """Find notes by title"""
        return self.session.query(Note)\
            .filter(Note.title.ilike(f"%{title}%"))\
            .all()
    
    def find_by_tags(self, tags: List[str]) -> List[Note]:
        """Find notes by tags"""
        return self.session.query(Note)\
            .join(Note.tags)\
            .filter(Tag.name.in_(tags))\
            .all()
    
    def search_content(self, search_term: str) -> List[Note]:
        """Search notes by content"""
        return self.session.query(Note)\
            .filter(Note.content.ilike(f"%{search_term}%"))\
            .all()
```

---

### **2. Unit of Work Pattern**

#### **Transaction Management**
```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class UnitOfWork:
    def __init__(self, engine):
        self.engine = engine
        self.session_factory = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self._session: Optional[AsyncSession] = None
    
    async def __aenter__(self):
        self._session = self.session_factory()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()
    
    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise RuntimeError("Unit of Work not started")
        return self._session
    
    async def commit(self):
        """Commit current transaction"""
        await self._session.commit()
    
    async def rollback(self):
        """Rollback current transaction"""
        await self._session.rollback()

class DatabaseService:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.uow = UnitOfWork(self.engine)
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        async with self.uow as uow:
            yield uow.session
    
    async def execute_in_transaction(self, operation):
        """Execute operation within transaction"""
        async with self.uow as uow:
            try:
                result = await operation(uow.session)
                await uow.commit()
                return result
            except Exception as e:
                await uow.rollback()
                raise e
```

---

### **3. Database Migration Pattern**

#### **Alembic Migration Management**
```python
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from sqlalchemy import create_engine

class DatabaseMigrationManager:
    def __init__(self, database_url: str, alembic_config_path: str = "alembic.ini"):
        self.database_url = database_url
        self.alembic_cfg = Config(alembic_config_path)
        self.alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        self.engine = create_engine(database_url)
    
    def create_migration(self, message: str) -> str:
        """Create a new migration"""
        try:
            command.revision(self.alembic_cfg, message=message, autogenerate=True)
            return f"Migration created: {message}"
        except Exception as e:
            return f"Error creating migration: {str(e)}"
    
    def upgrade_database(self, revision: str = "head") -> str:
        """Upgrade database to specified revision"""
        try:
            command.upgrade(self.alembic_cfg, revision)
            return f"Database upgraded to: {revision}"
        except Exception as e:
            return f"Error upgrading database: {str(e)}"
    
    def downgrade_database(self, revision: str) -> str:
        """Downgrade database to specified revision"""
        try:
            command.downgrade(self.alembic_cfg, revision)
            return f"Database downgraded to: {revision}"
        except Exception as e:
            return f"Error downgrading database: {str(e)}"
    
    def get_current_revision(self) -> str:
        """Get current database revision"""
        try:
            with self.engine.connect() as connection:
                context = EnvironmentContext(
                    self.alembic_cfg,
                    ScriptDirectory.from_config(self.alembic_cfg)
                )
                context.configure(connection=connection)
                return context.get_current_revision()
        except Exception as e:
            return f"Error getting current revision: {str(e)}"
    
    def get_migration_history(self) -> List[dict]:
        """Get migration history"""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            history = []
            
            for revision in script.walk_revisions():
                history.append({
                    "revision": revision.revision,
                    "down_revision": revision.down_revision,
                    "branch_labels": revision.branch_labels,
                    "depends_on": revision.depends_on,
                    "comment": revision.comment
                })
            
            return history
        except Exception as e:
            return [{"error": str(e)}]

# Migration CLI commands
class MigrationCLI:
    def __init__(self, migration_manager: DatabaseMigrationManager):
        self.migration_manager = migration_manager
    
    def create(self, message: str):
        """Create new migration"""
        result = self.migration_manager.create_migration(message)
        print(result)
    
    def upgrade(self, revision: str = "head"):
        """Upgrade database"""
        result = self.migration_manager.upgrade_database(revision)
        print(result)
    
    def downgrade(self, revision: str):
        """Downgrade database"""
        result = self.migration_manager.downgrade_database(revision)
        print(result)
    
    def status(self):
        """Show migration status"""
        current = self.migration_manager.get_current_revision()
        history = self.migration_manager.get_migration_history()
        
        print(f"Current revision: {current}")
        print("\nMigration history:")
        for migration in history:
            print(f"  {migration['revision']}: {migration['comment']}")
```

---

### **4. Database Connection Pooling Pattern**

#### **Connection Pool Management**
```python
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.engine import Engine
import threading
import time

class DatabaseConnectionPool:
    def __init__(self, database_url: str, pool_size: int = 20, max_overflow: int = 30):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine = self._create_engine()
        self._setup_connection_monitoring()
    
    def _create_engine(self) -> Engine:
        """Create database engine with connection pooling"""
        return create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False
        )
    
    def _setup_connection_monitoring(self):
        """Setup connection pool monitoring"""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set database pragmas on connection"""
            if "sqlite" in self.database_url:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout"""
            connection_record.info['checkout_time'] = time.time()
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin"""
            checkout_time = connection_record.info.get('checkout_time', 0)
            duration = time.time() - checkout_time
            if duration > 1.0:  # Log slow connections
                print(f"Slow connection: {duration:.2f}s")
    
    def get_connection_info(self) -> dict:
        """Get connection pool information"""
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    
    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            with self.engine.connect() as connection:
                connection.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    def close_all_connections(self):
        """Close all connections in pool"""
        self.engine.dispose()

class DatabaseHealthMonitor:
    def __init__(self, connection_pool: DatabaseConnectionPool):
        self.connection_pool = connection_pool
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: int = 60):
        """Start connection pool monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop connection pool monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: int):
        """Monitor connection pool in background"""
        while self.monitoring:
            try:
                info = self.connection_pool.get_connection_info()
                health = self.connection_pool.health_check()
                
                # Log pool status
                print(f"Pool Status: {info}, Health: {health}")
                
                # Alert on high connection usage
                if info["checked_out"] > self.connection_pool.pool_size * 0.8:
                    print("WARNING: High connection usage detected!")
                
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)
```

---

### **5. Database Sharding Pattern**

#### **Horizontal Database Sharding**
```python
from typing import Any, Dict, List
from hashlib import md5
import json

class DatabaseShardManager:
    def __init__(self, shard_configs: List[Dict[str, Any]]):
        self.shard_configs = shard_configs
        self.shard_engines = {}
        self._initialize_shards()
    
    def _initialize_shards(self):
        """Initialize database connections for all shards"""
        for config in self.shard_configs:
            shard_id = config["shard_id"]
            database_url = config["database_url"]
            self.shard_engines[shard_id] = create_engine(database_url)
    
    def get_shard_for_key(self, key: str) -> str:
        """Determine which shard to use for a given key"""
        hash_value = int(md5(key.encode()).hexdigest(), 16)
        shard_index = hash_value % len(self.shard_configs)
        return self.shard_configs[shard_index]["shard_id"]
    
    def get_shard_engine(self, shard_id: str):
        """Get database engine for specific shard"""
        return self.shard_engines.get(shard_id)
    
    def execute_on_shard(self, shard_id: str, operation, *args, **kwargs):
        """Execute operation on specific shard"""
        engine = self.get_shard_engine(shard_id)
        if not engine:
            raise ValueError(f"Shard {shard_id} not found")
        
        with engine.connect() as connection:
            return operation(connection, *args, **kwargs)
    
    def execute_on_all_shards(self, operation, *args, **kwargs) -> Dict[str, Any]:
        """Execute operation on all shards"""
        results = {}
        for shard_id in self.shard_engines.keys():
            try:
                result = self.execute_on_shard(shard_id, operation, *args, **kwargs)
                results[shard_id] = {"success": True, "result": result}
            except Exception as e:
                results[shard_id] = {"success": False, "error": str(e)}
        return results

class ShardedRepository:
    def __init__(self, shard_manager: DatabaseShardManager, model_class: type):
        self.shard_manager = shard_manager
        self.model_class = model_class
    
    def create(self, entity, shard_key: str = None):
        """Create entity on appropriate shard"""
        if not shard_key:
            shard_key = str(entity.id) if hasattr(entity, 'id') else str(hash(entity))
        
        shard_id = self.shard_manager.get_shard_for_key(shard_key)
        engine = self.shard_manager.get_shard_engine(shard_id)
        
        with engine.begin() as connection:
            connection.add(entity)
            connection.commit()
            connection.refresh(entity)
            return entity
    
    def get_by_id(self, entity_id: str, shard_key: str = None):
        """Get entity by ID from appropriate shard"""
        if not shard_key:
            shard_key = str(entity_id)
        
        shard_id = self.shard_manager.get_shard_for_key(shard_key)
        engine = self.shard_manager.get_shard_engine(shard_id)
        
        with engine.connect() as connection:
            return connection.query(self.model_class)\
                .filter(self.model_class.id == entity_id)\
                .first()
    
    def search_across_shards(self, criteria: Dict[str, Any]) -> List[Any]:
        """Search across all shards"""
        all_results = []
        results = self.shard_manager.execute_on_all_shards(
            self._search_operation, criteria
        )
        
        for shard_id, result in results.items():
            if result["success"]:
                all_results.extend(result["result"])
        
        return all_results
    
    def _search_operation(self, connection, criteria: Dict[str, Any]):
        """Search operation to execute on each shard"""
        query = connection.query(self.model_class)
        
        for field, value in criteria.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)
        
        return query.all()
```

---

### **6. Database Caching Pattern**

#### **Multi-Level Database Caching**
```python
import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta

class DatabaseCacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.local_cache = {}  # L1 cache
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "local_hits": 0,
            "redis_hits": 0
        }
    
    def _generate_cache_key(self, table: str, key: str, params: dict = None) -> str:
        """Generate cache key for database query"""
        key_data = f"{table}:{key}"
        if params:
            key_data += f":{json.dumps(params, sort_keys=True)}"
        return f"db_cache:{key_data}"
    
    def get(self, table: str, key: str, params: dict = None) -> Optional[Any]:
        """Get data from cache (L1 -> L2 -> None)"""
        cache_key = self._generate_cache_key(table, key, params)
        
        # Try L1 cache (local memory)
        if cache_key in self.local_cache:
            self.cache_stats["hits"] += 1
            self.cache_stats["local_hits"] += 1
            return self.local_cache[cache_key]
        
        # Try L2 cache (Redis)
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = pickle.loads(cached_data)
                # Store in L1 cache
                self.local_cache[cache_key] = data
                self.cache_stats["hits"] += 1
                self.cache_stats["redis_hits"] += 1
                return data
        except Exception as e:
            print(f"Redis cache error: {e}")
        
        self.cache_stats["misses"] += 1
        return None
    
    def set(self, table: str, key: str, data: Any, ttl: int = 300, params: dict = None):
        """Set data in cache (L1 + L2)"""
        cache_key = self._generate_cache_key(table, key, params)
        
        # Store in L1 cache
        self.local_cache[cache_key] = data
        
        # Store in L2 cache (Redis)
        try:
            serialized_data = pickle.dumps(data)
            self.redis_client.setex(cache_key, ttl, serialized_data)
        except Exception as e:
            print(f"Redis cache set error: {e}")
    
    def invalidate(self, table: str, pattern: str = "*"):
        """Invalidate cache entries"""
        cache_pattern = f"db_cache:{table}:{pattern}"
        
        # Clear L1 cache
        keys_to_remove = [k for k in self.local_cache.keys() if k.startswith(f"db_cache:{table}")]
        for key in keys_to_remove:
            del self.local_cache[key]
        
        # Clear L2 cache
        try:
            keys = self.redis_client.keys(cache_pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Redis cache invalidation error: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%"
        }

class CachedRepository:
    def __init__(self, base_repository, cache_manager: DatabaseCacheManager):
        self.base_repository = base_repository
        self.cache_manager = cache_manager
        self.cache_ttl = 300  # 5 minutes default
    
    def get_by_id(self, entity_id: Any) -> Optional[Any]:
        """Get entity by ID with caching"""
        cache_key = f"id_{entity_id}"
        cached_entity = self.cache_manager.get(
            self.base_repository.model_class.__tablename__,
            cache_key
        )
        
        if cached_entity:
            return cached_entity
        
        # Fetch from database
        entity = self.base_repository.get_by_id(entity_id)
        if entity:
            self.cache_manager.set(
                self.base_repository.model_class.__tablename__,
                cache_key,
                entity,
                self.cache_ttl
            )
        
        return entity
    
    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Any]:
        """Find entities by criteria with caching"""
        cache_key = f"criteria_{hash(str(sorted(criteria.items())))}"
        cached_results = self.cache_manager.get(
            self.base_repository.model_class.__tablename__,
            cache_key,
            criteria
        )
        
        if cached_results:
            return cached_results
        
        # Fetch from database
        results = self.base_repository.find_by_criteria(criteria)
        if results:
            self.cache_manager.set(
                self.base_repository.model_class.__tablename__,
                cache_key,
                results,
                self.cache_ttl,
                criteria
            )
        
        return results
    
    def create(self, entity: Any) -> Any:
        """Create entity and invalidate related cache"""
        result = self.base_repository.create(entity)
        self.cache_manager.invalidate(
            self.base_repository.model_class.__tablename__
        )
        return result
    
    def update(self, entity: Any) -> Any:
        """Update entity and invalidate related cache"""
        result = self.base_repository.update(entity)
        self.cache_manager.invalidate(
            self.base_repository.model_class.__tablename__
        )
        return result
    
    def delete(self, entity_id: Any) -> bool:
        """Delete entity and invalidate related cache"""
        result = self.base_repository.delete(entity_id)
        if result:
            self.cache_manager.invalidate(
                self.base_repository.model_class.__tablename__
            )
        return result
```

---

### **7. Database Backup Pattern**

#### **Automated Database Backup**
```python
import subprocess
import os
import gzip
from datetime import datetime, timedelta
from typing import List, Dict, Any
import schedule
import time

class DatabaseBackupManager:
    def __init__(self, database_config: Dict[str, Any], backup_config: Dict[str, Any]):
        self.database_config = database_config
        self.backup_config = backup_config
        self.backup_directory = backup_config["backup_directory"]
        self.retention_days = backup_config["retention_days"]
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self):
        """Ensure backup directory exists"""
        os.makedirs(self.backup_directory, exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create database backup"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = os.path.join(self.backup_directory, f"{backup_name}.sql")
        compressed_path = f"{backup_path}.gz"
        
        try:
            # Create database dump
            dump_command = self._build_dump_command(backup_path)
            result = subprocess.run(dump_command, check=True, capture_output=True, text=True)
            
            # Compress backup
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove uncompressed file
            os.remove(backup_path)
            
            # Create backup metadata
            self._create_backup_metadata(compressed_path, backup_name)
            
            return compressed_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Backup failed: {e.stderr}")
    
    def _build_dump_command(self, output_path: str) -> List[str]:
        """Build database dump command based on database type"""
        db_type = self.database_config["type"].lower()
        
        if db_type == "postgresql":
            return [
                "pg_dump",
                f"--host={self.database_config['host']}",
                f"--port={self.database_config['port']}",
                f"--username={self.database_config['username']}",
                f"--dbname={self.database_config['database']}",
                f"--file={output_path}",
                "--verbose",
                "--no-password"
            ]
        elif db_type == "mysql":
            return [
                "mysqldump",
                f"--host={self.database_config['host']}",
                f"--port={self.database_config['port']}",
                f"--user={self.database_config['username']}",
                f"--password={self.database_config['password']}",
                self.database_config["database"],
                f"--result-file={output_path}"
            ]
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _create_backup_metadata(self, backup_path: str, backup_name: str):
        """Create backup metadata file"""
        metadata = {
            "backup_name": backup_name,
            "backup_path": backup_path,
            "created_at": datetime.now().isoformat(),
            "database_config": {
                "type": self.database_config["type"],
                "host": self.database_config["host"],
                "database": self.database_config["database"]
            },
            "file_size": os.path.getsize(backup_path)
        }
        
        metadata_path = f"{backup_path}.metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            # Decompress if needed
            if backup_path.endswith('.gz'):
                decompressed_path = backup_path[:-3]
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(decompressed_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                backup_path = decompressed_path
            
            # Restore database
            restore_command = self._build_restore_command(backup_path)
            result = subprocess.run(restore_command, check=True, capture_output=True, text=True)
            
            # Clean up decompressed file if it was created
            if backup_path.endswith('.sql') and os.path.exists(backup_path):
                os.remove(backup_path)
            
            return True
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Restore failed: {e.stderr}")
    
    def _build_restore_command(self, backup_path: str) -> List[str]:
        """Build database restore command"""
        db_type = self.database_config["type"].lower()
        
        if db_type == "postgresql":
            return [
                "psql",
                f"--host={self.database_config['host']}",
                f"--port={self.database_config['port']}",
                f"--username={self.database_config['username']}",
                f"--dbname={self.database_config['database']}",
                f"--file={backup_path}",
                "--verbose"
            ]
        elif db_type == "mysql":
            return [
                "mysql",
                f"--host={self.database_config['host']}",
                f"--port={self.database_config['port']}",
                f"--user={self.database_config['username']}",
                f"--password={self.database_config['password']}",
                self.database_config["database"],
                f"< {backup_path}"
            ]
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for filename in os.listdir(self.backup_directory):
            if filename.startswith("backup_") and filename.endswith(".sql.gz"):
                file_path = os.path.join(self.backup_directory, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    print(f"Removed old backup: {filename}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for filename in os.listdir(self.backup_directory):
            if filename.startswith("backup_") and filename.endswith(".sql.gz"):
                file_path = os.path.join(self.backup_directory, filename)
                metadata_path = f"{file_path}.metadata.json"
                
                backup_info = {
                    "filename": filename,
                    "file_path": file_path,
                    "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    "file_size": os.path.getsize(file_path)
                }
                
                # Load metadata if available
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            backup_info.update(metadata)
                    except Exception as e:
                        print(f"Error loading metadata for {filename}: {e}")
                
                backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    def schedule_backups(self):
        """Schedule automated backups"""
        schedule.every().day.at("02:00").do(self.create_backup)
        schedule.every().day.at("02:30").do(self.cleanup_old_backups)
        
        print("Backup schedule configured:")
        print("- Daily backup at 02:00")
        print("- Cleanup at 02:30")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
```

---

### **8. Database Performance Monitoring Pattern**

#### **Query Performance Monitoring**
```python
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine
from typing import Dict, List, Any
import logging

class DatabasePerformanceMonitor:
    def __init__(self, slow_query_threshold: float = 1.0):
        self.slow_query_threshold = slow_query_threshold
        self.query_stats = []
        self.logger = logging.getLogger(__name__)
        self._setup_query_monitoring()
    
    def _setup_query_monitoring(self):
        """Setup query monitoring for all engines"""
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            
            query_info = {
                "statement": statement,
                "parameters": parameters,
                "duration": total_time,
                "timestamp": time.time(),
                "executemany": executemany
            }
            
            self.query_stats.append(query_info)
            
            # Log slow queries
            if total_time > self.slow_query_threshold:
                self.logger.warning(f"Slow query detected: {total_time:.2f}s - {statement[:100]}...")
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries"""
        return sorted(
            self.query_stats,
            key=lambda x: x["duration"],
            reverse=True
        )[:limit]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        if not self.query_stats:
            return {"message": "No queries recorded"}
        
        durations = [q["duration"] for q in self.query_stats]
        
        return {
            "total_queries": len(self.query_stats),
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "slow_queries": len([d for d in durations if d > self.slow_query_threshold])
        }
    
    def clear_stats(self):
        """Clear query statistics"""
        self.query_stats.clear()

class DatabaseIndexAnalyzer:
    def __init__(self, engine):
        self.engine = engine
    
    def analyze_table_indexes(self, table_name: str) -> Dict[str, Any]:
        """Analyze indexes for a specific table"""
        with self.engine.connect() as connection:
            # Get table information
            table_info = connection.execute(f"""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE tablename = '{table_name}'
                ORDER BY n_distinct DESC
            """).fetchall()
            
            # Get index information
            index_info = connection.execute(f"""
                SELECT 
                    indexname,
                    indexdef,
                    pg_size_pretty(pg_relation_size(indexname::regclass)) as size
                FROM pg_indexes 
                WHERE tablename = '{table_name}'
            """).fetchall()
            
            return {
                "table_name": table_name,
                "column_stats": [dict(row) for row in table_info],
                "indexes": [dict(row) for row in index_info]
            }
    
    def suggest_indexes(self, table_name: str) -> List[str]:
        """Suggest indexes based on query patterns"""
        suggestions = []
        
        with self.engine.connect() as connection:
            # Analyze query patterns
            query_stats = connection.execute(f"""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time
                FROM pg_stat_statements 
                WHERE query ILIKE '%{table_name}%'
                ORDER BY total_time DESC
                LIMIT 10
            """).fetchall()
            
            for query_stat in query_stats:
                query = query_stat[0]
                # Simple heuristic: suggest indexes for WHERE clauses
                if "WHERE" in query.upper():
                    # Extract column names from WHERE clause
                    where_clause = query.upper().split("WHERE")[1].split("ORDER BY")[0]
                    # This is a simplified example - real implementation would be more sophisticated
                    suggestions.append(f"Consider index on columns used in WHERE clause: {where_clause[:50]}...")
        
        return suggestions
```

---

## 🚀 **DATABASE OPTIMIZATION PATTERNS**

### **1. Query Optimization**
```python
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import func, desc, asc

class OptimizedQueries:
    def __init__(self, session):
        self.session = session
    
    def get_notes_with_tags_optimized(self, limit: int = 10):
        """Optimized query with eager loading"""
        return self.session.query(Note)\
            .options(joinedload(Note.tags))\
            .limit(limit)\
            .all()
    
    def get_notes_paginated(self, page: int = 1, per_page: int = 10):
        """Paginated query with count"""
        offset = (page - 1) * per_page
        
        # Get total count
        total = self.session.query(func.count(Note.id)).scalar()
        
        # Get paginated results
        notes = self.session.query(Note)\
            .offset(offset)\
            .limit(per_page)\
            .all()
        
        return {
            "notes": notes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
```

### **2. Database Connection Optimization**
```python
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

def create_optimized_engine(database_url: str):
    """Create optimized database engine"""
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        connect_args={
            "options": "-c default_transaction_isolation=read committed"
        }
    )
```

---

## 🔒 **DATABASE SECURITY PATTERNS**

### **1. SQL Injection Prevention**
```python
from sqlalchemy import text

class SecureQueryBuilder:
    def __init__(self, session):
        self.session = session
    
    def safe_search(self, search_term: str):
        """Safe parameterized query"""
        return self.session.execute(
            text("SELECT * FROM notes WHERE content ILIKE :search_term"),
            {"search_term": f"%{search_term}%"}
        ).fetchall()
```

### **2. Database Encryption**
```python
from cryptography.fernet import Fernet
import base64

class DatabaseEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_field(self, value: str) -> str:
        """Encrypt sensitive field"""
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt sensitive field"""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
```

---

**Last Updated:** September 6, 2025  
**Database Patterns Version:** 3.0.0  
**Status:** ✅ **PRODUCTION-READY**

**COMPREHENSIVE DATABASE PATTERNS COMPLETE!**
