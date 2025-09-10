# Cache Optimization Configuration
CACHE_CONFIG = {
    "embedding_cache": {
        "max_size": 1000,        # Limit cache entries
        "ttl": 3600,            # 1 hour TTL
        "eviction_policy": "lru", # Least Recently Used
        "cleanup_interval": 300   # Clean up every 5 minutes
    },
    "query_cache": {
        "max_size": 500,
        "ttl": 1800,            # 30 minutes TTL
        "eviction_policy": "lru",
        "cleanup_interval": 300
    },
    "search_cache": {
        "max_size": 200,
        "ttl": 900,             # 15 minutes TTL
        "eviction_policy": "lru",
        "cleanup_interval": 300
    }
}
