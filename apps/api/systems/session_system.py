"""
Real Session Management System
For DE-13: Session Hijacking & State Manipulation
"""
import redis
import secrets
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class SessionSystem:
    def __init__(self, redis_host: Optional[str] = None, redis_port: Optional[int] = None):
        ttl_env = os.getenv("SESSION_TTL_SECONDS")
        self.session_ttl_seconds = int(ttl_env) if ttl_env else 3600
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
            self.redis_client = None
            self.session_store = {}
        
        self.session_tokens = {}
    
    def create_session(self, user_id: str) -> str:
        """Create a new session"""
        session_token = f"session_{secrets.token_urlsafe(32)}"
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "state": {},
            "token": session_token
        }
        
        if self.redis_client:
            self.redis_client.setex(
                f"session:{session_token}",
                self.session_ttl_seconds,
                json.dumps(session_data)
            )
        else:
            self.session_store[session_token] = session_data
        
        self.session_tokens[user_id] = session_token
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session data"""
        if self.redis_client:
            data = self.redis_client.get(f"session:{session_token}")
            if data:
                return json.loads(data)
        else:
            return self.session_store.get(session_token)
        return None
    
    def update_session_state(self, session_token: str, state_updates: Dict) -> bool:
        """Update session state"""
        session = self.get_session(session_token)
        if not session:
            return False
        
        session["state"].update(state_updates)
        session["last_activity"] = datetime.now().isoformat()
        
        if self.redis_client:
            self.redis_client.setex(
                f"session:{session_token}",
                self.session_ttl_seconds,
                json.dumps(session)
            )
        else:
            self.session_store[session_token] = session
        
        return True
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions - potential leak point"""
        sessions = []
        if self.redis_client:
            keys = self.redis_client.keys("session:*")
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    sessions.append(json.loads(data))
        else:
            sessions = list(self.session_store.values())
        
        return sessions
    
    def get_session_by_user(self, user_id: str) -> Optional[str]:
        """Get session token for user - potential leak point"""
        return self.session_tokens.get(user_id)
