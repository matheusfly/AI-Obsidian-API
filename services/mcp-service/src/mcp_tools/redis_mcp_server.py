#!/usr/bin/env python3
"""
Redis MCP Server
Provides Redis database operations through MCP tools
"""

import asyncio
import json
import logging
import redis
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedisConfig(BaseModel):
    """Redis connection configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True

class RedisKeyValue(BaseModel):
    """Redis key-value pair"""
    key: str
    value: Union[str, int, float, bool, dict, list]
    ttl: Optional[int] = None

class RedisQuery(BaseModel):
    """Redis query parameters"""
    pattern: str = "*"
    count: int = 100
    cursor: int = 0

class RedisMCPTools:
    """Redis MCP Tools for database operations"""
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self.redis_client = None
        self.connect()
    
    def connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                decode_responses=self.config.decode_responses
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    async def redis_ping(self) -> Dict[str, Any]:
        """Ping Redis server to check connectivity"""
        try:
            if not self.is_connected():
                self.connect()
            
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis connection failed",
                    "timestamp": datetime.now().isoformat()
                }
            
            response = self.redis_client.ping()
            return {
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_set(self, key_value: RedisKeyValue) -> Dict[str, Any]:
        """Set a key-value pair in Redis"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Convert value to string if it's not already
            if isinstance(key_value.value, (dict, list)):
                value = json.dumps(key_value.value)
            else:
                value = str(key_value.value)
            
            # Set the key with optional TTL
            if key_value.ttl:
                result = self.redis_client.setex(key_value.key, key_value.ttl, value)
            else:
                result = self.redis_client.set(key_value.key, value)
            
            return {
                "success": result,
                "key": key_value.key,
                "value": value,
                "ttl": key_value.ttl,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_get(self, key: str) -> Dict[str, Any]:
        """Get a value from Redis by key"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            value = self.redis_client.get(key)
            
            if value is None:
                return {
                    "success": True,
                    "key": key,
                    "value": None,
                    "exists": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Try to parse as JSON if possible
            try:
                parsed_value = json.loads(value)
                return {
                    "success": True,
                    "key": key,
                    "value": parsed_value,
                    "exists": True,
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "key": key,
                    "value": value,
                    "exists": True,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_delete(self, key: str) -> Dict[str, Any]:
        """Delete a key from Redis"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            result = self.redis_client.delete(key)
            
            return {
                "success": True,
                "key": key,
                "deleted": bool(result),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_keys(self, query: RedisQuery) -> Dict[str, Any]:
        """Get keys matching a pattern from Redis"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            keys = self.redis_client.keys(query.pattern)
            
            # Apply count limit
            if query.count and len(keys) > query.count:
                keys = keys[:query.count]
            
            return {
                "success": True,
                "keys": keys,
                "count": len(keys),
                "pattern": query.pattern,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_exists(self, key: str) -> Dict[str, Any]:
        """Check if a key exists in Redis"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            exists = self.redis_client.exists(key)
            
            return {
                "success": True,
                "key": key,
                "exists": bool(exists),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_ttl(self, key: str) -> Dict[str, Any]:
        """Get TTL (time to live) for a key in Redis"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            ttl = self.redis_client.ttl(key)
            
            return {
                "success": True,
                "key": key,
                "ttl": ttl,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            info = self.redis_client.info()
            
            return {
                "success": True,
                "info": info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def redis_flushdb(self) -> Dict[str, Any]:
        """Flush current database"""
        try:
            if not self.is_connected():
                return {
                    "success": False,
                    "error": "Redis not connected",
                    "timestamp": datetime.now().isoformat()
                }
            
            result = self.redis_client.flushdb()
            
            return {
                "success": result,
                "message": "Database flushed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Create Redis MCP tools instance
redis_config = RedisConfig()
redis_tools = RedisMCPTools(redis_config)

# MCP Tool functions
async def redis_ping() -> Dict[str, Any]:
    """Ping Redis server to check connectivity"""
    return await redis_tools.redis_ping()

async def redis_set(key: str, value: Union[str, int, float, bool, dict, list], ttl: Optional[int] = None) -> Dict[str, Any]:
    """Set a key-value pair in Redis"""
    key_value = RedisKeyValue(key=key, value=value, ttl=ttl)
    return await redis_tools.redis_set(key_value)

async def redis_get(key: str) -> Dict[str, Any]:
    """Get a value from Redis by key"""
    return await redis_tools.redis_get(key)

async def redis_delete(key: str) -> Dict[str, Any]:
    """Delete a key from Redis"""
    return await redis_tools.redis_delete(key)

async def redis_keys(pattern: str = "*", count: int = 100) -> Dict[str, Any]:
    """Get keys matching a pattern from Redis"""
    query = RedisQuery(pattern=pattern, count=count)
    return await redis_tools.redis_keys(query)

async def redis_exists(key: str) -> Dict[str, Any]:
    """Check if a key exists in Redis"""
    return await redis_tools.redis_exists(key)

async def redis_ttl(key: str) -> Dict[str, Any]:
    """Get TTL (time to live) for a key in Redis"""
    return await redis_tools.redis_ttl(key)

async def redis_info() -> Dict[str, Any]:
    """Get Redis server information"""
    return await redis_tools.redis_info()

async def redis_flushdb() -> Dict[str, Any]:
    """Flush current database"""
    return await redis_tools.redis_flushdb()

if __name__ == "__main__":
    # Test Redis connection
    async def test_redis():
        print("Testing Redis MCP Tools...")
        
        # Test ping
        ping_result = await redis_ping()
        print(f"Ping result: {ping_result}")
        
        # Test set/get
        set_result = await redis_set("test_key", "test_value", ttl=60)
        print(f"Set result: {set_result}")
        
        get_result = await redis_get("test_key")
        print(f"Get result: {get_result}")
        
        # Test info
        info_result = await redis_info()
        print(f"Info result: {info_result}")
    
    asyncio.run(test_redis())
