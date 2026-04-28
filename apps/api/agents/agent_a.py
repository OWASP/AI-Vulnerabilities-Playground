"""
Agent-A: Multi-agent system component
Handles sensitive data and communicates with Agent-B
"""
import os
import secrets
from typing import Dict, Optional
import requests

class AgentA:
    def __init__(self, agent_b_url: Optional[str] = None):
        self.agent_b_url = agent_b_url or os.getenv("AGENT_B_URL")
        self.agent_b_token: Optional[str] = None
        self.sensitive_data: Dict[str, str] = {}
        self.communication_log: list = []
        
    def initialize(self, agent_b_token: str):
        """Initialize with Agent-B's token"""
        self.agent_b_token = agent_b_token
        self.sensitive_data["agent_b_token"] = agent_b_token
        
    def communicate_with_agent_b(self, message: str, data: Optional[Dict] = None) -> Dict:
        """
        Real communication with Agent-B
        This is where the vulnerability exists - token might leak through logs/errors
        """
        try:
            if not self.agent_b_url:
                return {"status": "error", "error": "AGENT_B_URL is not configured"}
            headers = {
                "Authorization": f"Bearer {self.agent_b_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": message,
                "data": data or {}
            }
            
            # Log communication (potential leak point)
            self.communication_log.append({
                "to": "Agent-B",
                "headers": headers,  # ⚠️ Token in headers - potential leak
                "payload": payload
            })
            
            # Try to communicate (if Agent-B is running)
            try:
                response = requests.post(
                    f"{self.agent_b_url}/api/process",
                    headers=headers,
                    json=payload,
                    timeout=2
                )
                return {"status": "success", "response": response.json()}
            except requests.exceptions.RequestException as e:
                # Error might leak token information
                error_msg = str(e)
                return {
                    "status": "error",
                    "error": error_msg,
                    "debug_info": {
                        "url": self.agent_b_url,
                        "token_preview": self.agent_b_token[:10] + "..." if self.agent_b_token else None
                    }
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_communication_log(self, include_headers: bool = False) -> list:
        """Get communication log - potential leak point"""
        if include_headers:
            return self.communication_log
        # Sanitize headers
        sanitized = []
        for entry in self.communication_log:
            sanitized_entry = entry.copy()
            if "headers" in sanitized_entry:
                sanitized_entry["headers"] = {"Authorization": "Bearer ***REDACTED***"}
            sanitized.append(sanitized_entry)
        return sanitized
    
    def process_user_request(self, user_request: str) -> str:
        """Process user request - main entry point"""
        # User can try to extract token through various means
        if "agent-b" in user_request.lower() or "token" in user_request.lower():
            # Trigger communication
            result = self.communicate_with_agent_b(user_request)
            return str(result)
        return "Agent-A: Processing your request..."
