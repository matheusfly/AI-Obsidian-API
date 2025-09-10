# 🚀 **CACHING PATTERNS & TECHNIQUES**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **PRODUCTION-READY CACHING ARCHITECTURE**

---

## 🎯 **CACHING ARCHITECTURE PHILOSOPHY**

The Data Vault Obsidian caching architecture implements **Multi-Level Caching** with **Intelligent Invalidation**, **Distributed Caching**, and **Cache-Aside Patterns** to optimize performance while maintaining data consistency across the microservices ecosystem.

### **Core Caching Principles**

- **Multi-Level Caching** - L1 (Memory), L2 (Redis), L3 (CDN)
- **Cache-Aside Pattern** - Application-managed caching
- **Write-Through Caching** - Synchronous cache updates
- **Write-Behind Caching** - Asynchronous cache updates
- **Cache Invalidation** - Intelligent cache invalidation strategies
- **Distributed Caching** - Cross-service cache sharing
- **Cache Warming** - Proactive cache population

---

## 🏗️ **CACHING ARCHITECTURE PATTERNS**

### **1. Multi-Level Caching Pattern**

#### **L1 Memory Cache Implementation**
```python
import threading
import time
from typing import Any, Optional, Dict, Callable
from collections import OrderedDict
import hashlib
import json

class L1MemoryCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()
        self.hit_count = 0
        self.miss_count = 0
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.timestamps:
            return True
        
        return time.time() - self.timestamps[key] > self.default_ttl
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            self._remove_entry(oldest_key)
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache and not self._is_expired(key):
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.hit_count += 1
                return value
            
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache"""
        with self.lock:
            # Remove if exists
            if key in self.cache:
                self._remove_entry(key)
            
            # Evict if necessary
            self._evict_lru()
            
            # Add new entry
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": f"{hit_rate:.2f}%",
            "memory_usage": sum(len(str(v)) for v in self.cache.values())
        }
```

#### **L2 Redis Cache Implementation**
```python
import redis
import json
import pickle
from typing import Any, Optional, Union, List
from datetime import timedelta

class L2RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 default_ttl: int = 3600, compression: bool = True):
        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.default_ttl = default_ttl
        self.compression = compression
        self.namespace = "dvo_cache"
        self.hit_count = 0
        self.miss_count = 0
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        if self.compression:
            return pickle.dumps(value)
        else:
            return json.dumps(value, default=str).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        if self.compression:
            return pickle.loads(data)
        else:
            return json.loads(data.decode('utf-8'))
    
    def _get_key(self, key: str) -> str:
        """Get namespaced key"""
        return f"{self.namespace}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            redis_key = self._get_key(key)
            data = self.redis_client.get(redis_key)
            
            if data:
                self.hit_count += 1
                return self._deserialize(data)
            else:
                self.miss_count += 1
                return None
        except Exception as e:
            print(f"Redis cache get error: {e}")
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in Redis cache"""
        try:
            redis_key = self._get_key(key)
            data = self._serialize(value)
            ttl = ttl or self.default_ttl
            
            return self.redis_client.setex(redis_key, ttl, data)
        except Exception as e:
            print(f"Redis cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            redis_key = self._get_key(key)
            return bool(self.redis_client.delete(redis_key))
        except Exception as e:
            print(f"Redis cache delete error: {e}")
            return False
    
    def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple values from Redis cache"""
        try:
            redis_keys = [self._get_key(key) for key in keys]
            data_list = self.redis_client.mget(redis_keys)
            
            results = []
            for data in data_list:
                if data:
                    results.append(self._deserialize(data))
                    self.hit_count += 1
                else:
                    results.append(None)
                    self.miss_count += 1
            
            return results
        except Exception as e:
            print(f"Redis cache mget error: {e}")
            return [None] * len(keys)
    
    def mset(self, mapping: Dict[str, Any], ttl: int = None) -> bool:
        """Set multiple values in Redis cache"""
        try:
            redis_mapping = {self._get_key(k): self._serialize(v) for k, v in mapping.items()}
            
            if ttl:
                # Use pipeline for atomic operations
                pipe = self.redis_client.pipeline()
                for key, value in redis_mapping.items():
                    pipe.setex(key, ttl, value)
                pipe.execute()
            else:
                self.redis_client.mset(redis_mapping)
            
            return True
        except Exception as e:
            print(f"Redis cache mset error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern"""
        try:
            search_pattern = self._get_key(pattern)
            keys = self.redis_client.keys(search_pattern)
            
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis cache pattern invalidation error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        try:
            info = self.redis_client.info('memory')
            memory_usage = info.get('used_memory', 0)
        except:
            memory_usage = 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": f"{hit_rate:.2f}%",
            "memory_usage": memory_usage,
            "redis_info": self.redis_client.info()
        }
```

#### **Multi-Level Cache Manager**
```python
class MultiLevelCacheManager:
    def __init__(self, l1_cache: L1MemoryCache, l2_cache: L2RedisCache):
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache
        self.cache_hierarchy = ["l1", "l2"]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache hierarchy (L1 -> L2)"""
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            return value
        
        # Try L2 cache
        value = self.l2_cache.get(key)
        if value is not None:
            # Populate L1 cache
            self.l1_cache.set(key, value)
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in all cache levels"""
        # Set in L1 cache
        self.l1_cache.set(key, value, ttl)
        
        # Set in L2 cache
        self.l2_cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete value from all cache levels"""
        l1_deleted = self.l1_cache.delete(key)
        l2_deleted = self.l2_cache.delete(key)
        return l1_deleted or l2_deleted
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern in all levels"""
        l1_count = 0
        l2_count = self.l2_cache.invalidate_pattern(pattern)
        
        # L1 cache doesn't support pattern matching, so we clear it
        # In production, you might want to implement pattern matching for L1
        self.l1_cache.clear()
        
        return l1_count + l2_count
    
    def get_combined_stats(self) -> Dict[str, Any]:
        """Get combined statistics from all cache levels"""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = self.l2_cache.get_stats()
        
        return {
            "l1_cache": l1_stats,
            "l2_cache": l2_stats,
            "total_hits": l1_stats["hit_count"] + l2_stats["hit_count"],
            "total_misses": l1_stats["miss_count"] + l2_stats["miss_count"]
        }
```

---

### **2. Cache-Aside Pattern**

#### **Application-Managed Caching**
```python
from typing import Callable, Any, Optional
import asyncio
import time

class CacheAsideManager:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.cache_misses = 0
        self.cache_hits = 0
    
    async def get_or_set(self, key: str, fetch_func: Callable, ttl: int = None) -> Any:
        """Get from cache or fetch and cache the result"""
        # Try to get from cache
        cached_value = self.cache_manager.get(key)
        
        if cached_value is not None:
            self.cache_hits += 1
            return cached_value
        
        # Cache miss - fetch from source
        self.cache_misses += 1
        value = await fetch_func()
        
        # Cache the result
        if value is not None:
            self.cache_manager.set(key, value, ttl)
        
        return value
    
    def get_or_set_sync(self, key: str, fetch_func: Callable, ttl: int = None) -> Any:
        """Synchronous version of get_or_set"""
        # Try to get from cache
        cached_value = self.cache_manager.get(key)
        
        if cached_value is not None:
            self.cache_hits += 1
            return cached_value
        
        # Cache miss - fetch from source
        self.cache_misses += 1
        value = fetch_func()
        
        # Cache the result
        if value is not None:
            self.cache_manager.set(key, value, ttl)
        
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache-aside statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests
        }

# Example usage with database operations
class CachedNoteRepository:
    def __init__(self, db_repository, cache_manager: CacheAsideManager):
        self.db_repository = db_repository
        self.cache_manager = cache_manager
    
    async def get_note_by_id(self, note_id: str) -> Optional[dict]:
        """Get note by ID with caching"""
        cache_key = f"note:{note_id}"
        
        async def fetch_note():
            return await self.db_repository.get_by_id(note_id)
        
        return await self.cache_manager.get_or_set(
            cache_key, 
            fetch_note, 
            ttl=3600  # 1 hour
        )
    
    async def search_notes(self, query: str) -> List[dict]:
        """Search notes with caching"""
        cache_key = f"search:{hash(query)}"
        
        async def fetch_search_results():
            return await self.db_repository.search(query)
        
        return await self.cache_manager.get_or_set(
            cache_key,
            fetch_search_results,
            ttl=1800  # 30 minutes
        )
```

---

### **3. Write-Through Caching Pattern**

#### **Synchronous Cache Updates**
```python
class WriteThroughCacheManager:
    def __init__(self, cache_manager: MultiLevelCacheManager, 
                 write_func: Callable[[str, Any], bool]):
        self.cache_manager = cache_manager
        self.write_func = write_func
        self.write_errors = 0
        self.write_successes = 0
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Write through to both cache and persistent storage"""
        try:
            # Write to persistent storage first
            success = self.write_func(key, value)
            
            if success:
                # Write to cache
                self.cache_manager.set(key, value, ttl)
                self.write_successes += 1
                return True
            else:
                self.write_errors += 1
                return False
                
        except Exception as e:
            print(f"Write-through error: {e}")
            self.write_errors += 1
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get write-through statistics"""
        total_writes = self.write_successes + self.write_errors
        success_rate = (self.write_successes / total_writes * 100) if total_writes > 0 else 0
        
        return {
            "write_successes": self.write_successes,
            "write_errors": self.write_errors,
            "success_rate": f"{success_rate:.2f}%",
            "total_writes": total_writes
        }

# Example with database write-through
class WriteThroughNoteRepository:
    def __init__(self, db_repository, cache_manager: WriteThroughCacheManager):
        self.db_repository = db_repository
        self.cache_manager = cache_manager
    
    async def create_note(self, note_data: dict) -> dict:
        """Create note with write-through caching"""
        note_id = note_data.get("id")
        cache_key = f"note:{note_id}"
        
        # Write to database
        created_note = await self.db_repository.create(note_data)
        
        # Write to cache
        self.cache_manager.set(cache_key, created_note)
        
        return created_note
    
    async def update_note(self, note_id: str, note_data: dict) -> dict:
        """Update note with write-through caching"""
        cache_key = f"note:{note_id}"
        
        # Update in database
        updated_note = await self.db_repository.update(note_id, note_data)
        
        # Update in cache
        self.cache_manager.set(cache_key, updated_note)
        
        return updated_note
```

---

### **4. Write-Behind Caching Pattern**

#### **Asynchronous Cache Updates**
```python
import asyncio
from asyncio import Queue
from typing import Dict, Any, Callable
import time

class WriteBehindCacheManager:
    def __init__(self, cache_manager: MultiLevelCacheManager, 
                 write_func: Callable[[str, Any], bool],
                 batch_size: int = 100,
                 flush_interval: int = 60):
        self.cache_manager = cache_manager
        self.write_func = write_func
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.write_queue = Queue()
        self.pending_writes = {}
        self.write_errors = 0
        self.write_successes = 0
        self.is_running = False
        self.flush_task = None
    
    async def start(self):
        """Start the write-behind processor"""
        self.is_running = True
        self.flush_task = asyncio.create_task(self._flush_loop())
    
    async def stop(self):
        """Stop the write-behind processor"""
        self.is_running = False
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache and queue for write-behind"""
        # Write to cache immediately
        self.cache_manager.set(key, value, ttl)
        
        # Queue for write-behind
        self.pending_writes[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    async def _flush_loop(self):
        """Background loop for processing write-behind operations"""
        while self.is_running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_pending_writes()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Write-behind flush error: {e}")
    
    async def _flush_pending_writes(self):
        """Flush pending writes to persistent storage"""
        if not self.pending_writes:
            return
        
        # Process in batches
        items = list(self.pending_writes.items())
        batches = [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]
        
        for batch in batches:
            await self._process_batch(batch)
    
    async def _process_batch(self, batch: List[tuple]):
        """Process a batch of write-behind operations"""
        for key, data in batch:
            try:
                success = await self.write_func(key, data["value"])
                
                if success:
                    self.write_successes += 1
                    # Remove from pending writes
                    if key in self.pending_writes:
                        del self.pending_writes[key]
                else:
                    self.write_errors += 1
                    
            except Exception as e:
                print(f"Write-behind error for key {key}: {e}")
                self.write_errors += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get write-behind statistics"""
        total_writes = self.write_successes + self.write_errors
        success_rate = (self.write_successes / total_writes * 100) if total_writes > 0 else 0
        
        return {
            "write_successes": self.write_successes,
            "write_errors": self.write_errors,
            "success_rate": f"{success_rate:.2f}%",
            "total_writes": total_writes,
            "pending_writes": len(self.pending_writes)
        }
```

---

### **5. Cache Invalidation Patterns**

#### **Time-Based Invalidation**
```python
class TimeBasedInvalidation:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.ttl_configs = {}
    
    def set_ttl(self, pattern: str, ttl: int):
        """Set TTL for cache entries matching pattern"""
        self.ttl_configs[pattern] = ttl
    
    def get_ttl(self, key: str) -> int:
        """Get TTL for a specific key"""
        for pattern, ttl in self.ttl_configs.items():
            if self._matches_pattern(key, pattern):
                return ttl
        return 3600  # Default TTL
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)

class EventBasedInvalidation:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.invalidation_rules = {}
    
    def add_invalidation_rule(self, event_type: str, cache_pattern: str):
        """Add invalidation rule for event type"""
        if event_type not in self.invalidation_rules:
            self.invalidation_rules[event_type] = []
        self.invalidation_rules[event_type].append(cache_pattern)
    
    def handle_event(self, event_type: str, event_data: dict):
        """Handle invalidation event"""
        if event_type in self.invalidation_rules:
            for pattern in self.invalidation_rules[event_type]:
                # Replace placeholders in pattern with event data
                resolved_pattern = self._resolve_pattern(pattern, event_data)
                self.cache_manager.invalidate_pattern(resolved_pattern)
    
    def _resolve_pattern(self, pattern: str, event_data: dict) -> str:
        """Resolve pattern placeholders with event data"""
        resolved = pattern
        for key, value in event_data.items():
            resolved = resolved.replace(f"{{{key}}}", str(value))
        return resolved

class DependencyBasedInvalidation:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.dependencies = {}  # key -> set of dependent keys
    
    def add_dependency(self, key: str, dependent_key: str):
        """Add dependency relationship"""
        if key not in self.dependencies:
            self.dependencies[key] = set()
        self.dependencies[key].add(dependent_key)
    
    def invalidate_with_dependencies(self, key: str):
        """Invalidate key and all its dependencies"""
        # Invalidate the key itself
        self.cache_manager.delete(key)
        
        # Invalidate all dependent keys
        if key in self.dependencies:
            for dependent_key in self.dependencies[key]:
                self.cache_manager.delete(dependent_key)
                # Recursively invalidate dependencies of dependent keys
                self.invalidate_with_dependencies(dependent_key)
```

---

### **6. Distributed Caching Pattern**

#### **Cache Cluster Management**
```python
import hashlib
from typing import List, Dict, Any, Optional
import asyncio

class DistributedCacheManager:
    def __init__(self, cache_nodes: List[L2RedisCache]):
        self.cache_nodes = cache_nodes
        self.node_count = len(cache_nodes)
        self.consistent_hash = ConsistentHash(self.node_count)
    
    def _get_node(self, key: str) -> L2RedisCache:
        """Get cache node for a specific key"""
        node_index = self.consistent_hash.get_node(key)
        return self.cache_nodes[node_index]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        node = self._get_node(key)
        return node.get(key)
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in distributed cache"""
        node = self._get_node(key)
        return node.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete value from distributed cache"""
        node = self._get_node(key)
        return node.delete(key)
    
    def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple values from distributed cache"""
        # Group keys by node
        node_keys = {}
        for key in keys:
            node = self._get_node(key)
            node_id = id(node)
            if node_id not in node_keys:
                node_keys[node_id] = {"node": node, "keys": []}
            node_keys[node_id]["keys"].append(key)
        
        # Fetch from each node
        results = {}
        for node_data in node_keys.values():
            node = node_data["node"]
            keys = node_data["keys"]
            values = node.mget(keys)
            
            for key, value in zip(keys, values):
                results[key] = value
        
        # Return in original order
        return [results.get(key) for key in keys]
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate pattern across all nodes"""
        total_invalidated = 0
        for node in self.cache_nodes:
            total_invalidated += node.invalidate_pattern(pattern)
        return total_invalidated
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get statistics from all cache nodes"""
        node_stats = []
        for i, node in enumerate(self.cache_nodes):
            stats = node.get_stats()
            stats["node_id"] = i
            node_stats.append(stats)
        
        return {
            "nodes": node_stats,
            "total_nodes": self.node_count
        }

class ConsistentHash:
    def __init__(self, node_count: int, virtual_nodes: int = 150):
        self.node_count = node_count
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()
    
    def _build_ring(self):
        """Build consistent hash ring"""
        for i in range(self.node_count):
            for j in range(self.virtual_nodes):
                virtual_key = f"node_{i}_virtual_{j}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = i
                self.sorted_keys.append(hash_value)
        
        self.sorted_keys.sort()
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def get_node(self, key: str) -> int:
        """Get node index for a key"""
        hash_value = self._hash(key)
        
        # Find the first node with hash >= key hash
        for ring_key in self.sorted_keys:
            if ring_key >= hash_value:
                return self.ring[ring_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]
```

---

### **7. Cache Warming Pattern**

#### **Proactive Cache Population**
```python
import asyncio
from typing import List, Callable, Dict, Any
import time

class CacheWarmer:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.warming_tasks = {}
        self.warming_stats = {
            "total_warmed": 0,
            "warm_errors": 0,
            "warm_duration": 0
        }
    
    def add_warming_task(self, task_name: str, 
                        key_generator: Callable[[], List[str]],
                        data_fetcher: Callable[[str], Any],
                        interval: int = 3600):
        """Add a cache warming task"""
        self.warming_tasks[task_name] = {
            "key_generator": key_generator,
            "data_fetcher": data_fetcher,
            "interval": interval,
            "last_run": 0
        }
    
    async def start_warming(self):
        """Start all warming tasks"""
        tasks = []
        for task_name, task_config in self.warming_tasks.items():
            task = asyncio.create_task(self._warming_loop(task_name, task_config))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def _warming_loop(self, task_name: str, task_config: Dict[str, Any]):
        """Warming loop for a specific task"""
        while True:
            try:
                current_time = time.time()
                if current_time - task_config["last_run"] >= task_config["interval"]:
                    await self._warm_cache(task_name, task_config)
                    task_config["last_run"] = current_time
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Warming task {task_name} error: {e}")
                self.warming_stats["warm_errors"] += 1
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _warm_cache(self, task_name: str, task_config: Dict[str, Any]):
        """Warm cache for a specific task"""
        start_time = time.time()
        
        try:
            # Generate keys to warm
            keys = task_config["key_generator"]()
            
            # Warm each key
            for key in keys:
                try:
                    # Check if already cached
                    if self.cache_manager.get(key) is None:
                        # Fetch and cache data
                        data = await task_config["data_fetcher"](key)
                        if data is not None:
                            self.cache_manager.set(key, data)
                            self.warming_stats["total_warmed"] += 1
                
                except Exception as e:
                    print(f"Error warming key {key}: {e}")
                    self.warming_stats["warm_errors"] += 1
            
            duration = time.time() - start_time
            self.warming_stats["warm_duration"] += duration
            
            print(f"Warmed {len(keys)} keys for task {task_name} in {duration:.2f}s")
            
        except Exception as e:
            print(f"Error in warming task {task_name}: {e}")
            self.warming_stats["warm_errors"] += 1

class PredictiveCacheWarmer:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.access_patterns = {}
        self.prediction_model = None
    
    def record_access(self, key: str, timestamp: float = None):
        """Record cache access for pattern analysis"""
        if timestamp is None:
            timestamp = time.time()
        
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        
        self.access_patterns[key].append(timestamp)
    
    def predict_next_access(self, key: str) -> Optional[float]:
        """Predict when key will be accessed next"""
        if key not in self.access_patterns or len(self.access_patterns[key]) < 2:
            return None
        
        # Simple linear prediction based on access intervals
        accesses = self.access_patterns[key]
        intervals = [accesses[i] - accesses[i-1] for i in range(1, len(accesses))]
        
        if not intervals:
            return None
        
        avg_interval = sum(intervals) / len(intervals)
        last_access = accesses[-1]
        
        return last_access + avg_interval
    
    async def preload_predictive_keys(self, data_fetcher: Callable[[str], Any]):
        """Preload keys that are predicted to be accessed soon"""
        current_time = time.time()
        preload_threshold = 300  # 5 minutes
        
        for key in self.access_patterns:
            next_access = self.predict_next_access(key)
            if next_access and (next_access - current_time) <= preload_threshold:
                # Preload this key
                if self.cache_manager.get(key) is None:
                    try:
                        data = await data_fetcher(key)
                        if data is not None:
                            self.cache_manager.set(key, data)
                            print(f"Preloaded key: {key}")
                    except Exception as e:
                        print(f"Error preloading key {key}: {e}")
```

---

### **8. Cache Monitoring Pattern**

#### **Comprehensive Cache Monitoring**
```python
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CacheMetrics:
    timestamp: datetime
    hit_rate: float
    miss_rate: float
    total_requests: int
    memory_usage: int
    cache_size: int
    avg_response_time: float

class CacheMonitor:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.metrics_history = []
        self.alert_thresholds = {
            "hit_rate_min": 0.8,  # 80% minimum hit rate
            "memory_usage_max": 1024 * 1024 * 1024,  # 1GB max memory
            "response_time_max": 0.1  # 100ms max response time
        }
        self.alerts = []
    
    def collect_metrics(self) -> CacheMetrics:
        """Collect current cache metrics"""
        stats = self.cache_manager.get_combined_stats()
        
        total_requests = stats["total_hits"] + stats["total_misses"]
        hit_rate = stats["total_hits"] / total_requests if total_requests > 0 else 0
        miss_rate = 1 - hit_rate
        
        # Calculate average response time (simplified)
        avg_response_time = 0.01  # Placeholder - would need actual timing
        
        metrics = CacheMetrics(
            timestamp=datetime.now(),
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            total_requests=total_requests,
            memory_usage=stats.get("memory_usage", 0),
            cache_size=stats.get("size", 0),
            avg_response_time=avg_response_time
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def check_alerts(self, metrics: CacheMetrics) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        if metrics.hit_rate < self.alert_thresholds["hit_rate_min"]:
            alerts.append(f"Low hit rate: {metrics.hit_rate:.2%}")
        
        if metrics.memory_usage > self.alert_thresholds["memory_usage_max"]:
            alerts.append(f"High memory usage: {metrics.memory_usage / 1024 / 1024:.1f}MB")
        
        if metrics.avg_response_time > self.alert_thresholds["response_time_max"]:
            alerts.append(f"Slow response time: {metrics.avg_response_time:.3f}s")
        
        self.alerts.extend(alerts)
        return alerts
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {"message": "No metrics available"}
        
        hit_rates = [m.hit_rate for m in recent_metrics]
        memory_usage = [m.memory_usage for m in recent_metrics]
        response_times = [m.avg_response_time for m in recent_metrics]
        
        return {
            "period_hours": hours,
            "data_points": len(recent_metrics),
            "avg_hit_rate": sum(hit_rates) / len(hit_rates),
            "min_hit_rate": min(hit_rates),
            "max_hit_rate": max(hit_rates),
            "avg_memory_usage": sum(memory_usage) / len(memory_usage),
            "max_memory_usage": max(memory_usage),
            "avg_response_time": sum(response_times) / len(response_times),
            "max_response_time": max(response_times),
            "total_requests": sum(m.total_requests for m in recent_metrics),
            "recent_alerts": self.alerts[-10:]  # Last 10 alerts
        }
    
    def generate_report(self) -> str:
        """Generate cache performance report"""
        summary = self.get_metrics_summary(24)
        
        report = f"""
Cache Performance Report
========================
Period: Last 24 hours
Data Points: {summary['data_points']}

Performance Metrics:
- Average Hit Rate: {summary['avg_hit_rate']:.2%}
- Hit Rate Range: {summary['min_hit_rate']:.2%} - {summary['max_hit_rate']:.2%}
- Average Memory Usage: {summary['avg_memory_usage'] / 1024 / 1024:.1f} MB
- Peak Memory Usage: {summary['max_memory_usage'] / 1024 / 1024:.1f} MB
- Average Response Time: {summary['avg_response_time']:.3f}s
- Peak Response Time: {summary['max_response_time']:.3f}s
- Total Requests: {summary['total_requests']:,}

Recent Alerts:
{chr(10).join(f"- {alert}" for alert in summary['recent_alerts']) if summary['recent_alerts'] else "- No alerts"}
        """
        
        return report.strip()
```

---

## 🚀 **CACHE OPTIMIZATION PATTERNS**

### **1. Cache Key Optimization**
```python
class CacheKeyOptimizer:
    def __init__(self):
        self.key_patterns = {}
    
    def generate_optimized_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate optimized cache key"""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        
        # Create key components
        components = [prefix]
        components.extend(str(arg) for arg in args)
        components.extend(f"{k}:{v}" for k, v in sorted_kwargs)
        
        # Join with separator and hash if too long
        key = ":".join(components)
        if len(key) > 250:  # Redis key length limit
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{key_hash}"
        
        return key
    
    def register_pattern(self, pattern_name: str, key_template: str):
        """Register a key pattern for reuse"""
        self.key_patterns[pattern_name] = key_template
    
    def generate_from_pattern(self, pattern_name: str, **kwargs) -> str:
        """Generate key from registered pattern"""
        if pattern_name not in self.key_patterns:
            raise ValueError(f"Pattern {pattern_name} not found")
        
        template = self.key_patterns[pattern_name]
        return template.format(**kwargs)
```

### **2. Cache Compression**
```python
import gzip
import pickle
from typing import Any

class CacheCompressor:
    def __init__(self, compression_threshold: int = 1024):
        self.compression_threshold = compression_threshold
    
    def compress_if_needed(self, data: Any) -> tuple[bytes, bool]:
        """Compress data if it exceeds threshold"""
        serialized = pickle.dumps(data)
        
        if len(serialized) > self.compression_threshold:
            compressed = gzip.compress(serialized)
            return compressed, True
        
        return serialized, False
    
    def decompress_if_needed(self, data: bytes, was_compressed: bool) -> Any:
        """Decompress data if it was compressed"""
        if was_compressed:
            decompressed = gzip.decompress(data)
            return pickle.loads(decompressed)
        else:
            return pickle.loads(data)
```

---

## 🔒 **CACHE SECURITY PATTERNS**

### **1. Cache Encryption**
```python
from cryptography.fernet import Fernet
import base64

class CacheEncryption:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_sensitive_data(self, data: Any) -> bytes:
        """Encrypt sensitive data before caching"""
        serialized = pickle.dumps(data)
        return self.cipher.encrypt(serialized)
    
    def decrypt_sensitive_data(self, encrypted_data: bytes) -> Any:
        """Decrypt sensitive data from cache"""
        decrypted = self.cipher.decrypt(encrypted_data)
        return pickle.loads(decrypted)
```

### **2. Cache Access Control**
```python
class CacheAccessController:
    def __init__(self, cache_manager: MultiLevelCacheManager):
        self.cache_manager = cache_manager
        self.access_rules = {}
    
    def add_access_rule(self, key_pattern: str, allowed_roles: List[str]):
        """Add access control rule for key pattern"""
        self.access_rules[key_pattern] = allowed_roles
    
    def can_access(self, key: str, user_roles: List[str]) -> bool:
        """Check if user can access cache key"""
        for pattern, allowed_roles in self.access_rules.items():
            if self._matches_pattern(key, pattern):
                return any(role in user_roles for role in allowed_roles)
        return True  # Default allow if no rules match
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
```

---

**Last Updated:** September 6, 2025  
**Caching Patterns Version:** 3.0.0  
**Status:** ✅ **PRODUCTION-READY**

**COMPREHENSIVE CACHING PATTERNS COMPLETE!**
