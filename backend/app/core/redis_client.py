"""Redis client for caching and session management."""
import redis
from typing import Optional
import json
import os

class RedisClient:
    """Redis client wrapper with utility methods."""
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        # Using decode_responses=True to avoid manual decoding everywhere
        try:
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5  # Fail fast if Redis is down
            )
            # Test connection
            self.client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis connection failed: {e}. Running without cache.")
            self.client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        if not self.enabled or not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            # Fail gracefully if Redis is down - not ideal but works
            print(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: str, expire: int = 300):
        """Set a value in Redis with expiration (default 5 minutes)."""
        if not self.enabled or not self.client:
            return False
        try:
            self.client.setex(key, expire, value)
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[dict]:
        """Get and deserialize JSON from Redis."""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    def set_json(self, key: str, value: dict, expire: int = 300):
        """Serialize and set JSON in Redis."""
        try:
            serialized = json.dumps(value)
            return self.set(key, serialized, expire)
        except Exception as e:
            print(f"Redis JSON SET error: {e}")
            return False
    
    def delete(self, key: str):
        """Delete a key from Redis."""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in Redis."""
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            print(f"Redis INCREMENT error: {e}")
            return None

# Global Redis client instance
redis_client = RedisClient()
