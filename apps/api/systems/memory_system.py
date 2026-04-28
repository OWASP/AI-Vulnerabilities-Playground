"""
Real Memory System using Redis + Vector Database
For DE-03: Memory/Context Poisoning
"""
import redis
import json
import secrets
import os
from typing import Dict, List, Optional
from datetime import datetime

class MemorySystem:
    def __init__(self, redis_host: Optional[str] = None, redis_port: Optional[int] = None):
        ttl_env = os.getenv("MEMORY_TTL_SECONDS")
        self.memory_ttl_seconds = int(ttl_env) if ttl_env else 3600
        try:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
            else:
                host = redis_host or os.getenv("REDIS_HOST")
                port_env = os.getenv("REDIS_PORT")
                port = redis_port or (int(port_env) if port_env else None)
                if not host or not port:
                    raise ValueError("REDIS_URL or REDIS_HOST+REDIS_PORT not configured")
                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    decode_responses=True
                )
            self.redis_client.ping()
        except:
            # Fallback to in-memory if Redis not available
            self.redis_client = None
            self.memory_store = {}
        
        self.vector_memory = {}  # Simplified vector store
        
    def store(self, key: str, value: str, metadata: Optional[Dict] = None):
        """Store data in memory"""
        data = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if self.redis_client:
            self.redis_client.setex(
                f"memory:{key}",
                self.memory_ttl_seconds,
                json.dumps(data)
            )
        else:
            self.memory_store[key] = data
    
    def retrieve(self, key: str) -> Optional[Dict]:
        """Retrieve data from memory"""
        if self.redis_client:
            data = self.redis_client.get(f"memory:{key}")
            if data:
                return json.loads(data)
        else:
            return self.memory_store.get(key)
        return None
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search memory - potential leak point"""
        results = []
        
        # Search in-memory store
        search_store = self.memory_store if not self.redis_client else {}
        if self.redis_client:
            # Get all keys
            keys = self.redis_client.keys("memory:*")
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    search_store[key] = json.loads(data)
        
        # Simple keyword search
        query_lower = query.lower()
        for key, data in search_store.items():
            if query_lower in str(data).lower():
                results.append({
                    "key": key,
                    "data": data,
                    "relevance": 1.0
                })
        
        return results[:limit]
    
    def store_user_record(self, user_id: str, secret_code: str):
        """Store user confidential record"""
        self.store(
            f"user:{user_id}:confidential",
            secret_code,
            {"type": "confidential", "user_id": user_id}
        )
    
    def recall_user_data(self, user_id: str) -> Optional[str]:
        """Recall user data - potential leak point"""
        record = self.retrieve(f"user:{user_id}:confidential")
        if record:
            return record.get("value")
        return None
    
    def summarize_memory(self) -> str:
        """Summarize all memory - potential leak point"""
        all_data = []
        if self.redis_client:
            keys = self.redis_client.keys("memory:*")
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    all_data.append(json.loads(data))
        else:
            all_data = list(self.memory_store.values())
        
        return json.dumps(all_data, indent=2)
