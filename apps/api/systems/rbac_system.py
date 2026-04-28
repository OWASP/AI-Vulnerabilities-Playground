"""
Real Role-Based Access Control System
For DE-08: Agent Role Confusion
"""
import secrets
from typing import Dict, Optional, List
from enum import Enum

class AgentRole(Enum):
    SUPPORT = "support"
    ADMIN = "admin"
    ANALYZER = "analyzer"

class RBACSystem:
    def __init__(self):
        self.agents = {}
        self.role_permissions = {
            AgentRole.SUPPORT: ["view_tickets", "respond_to_users"],
            AgentRole.ADMIN: ["view_tickets", "respond_to_users", "manage_system", "access_admin_keys"],
            AgentRole.ANALYZER: ["analyze_data", "generate_reports"]
        }
        self.admin_keys = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agents with roles"""
        admin_key = f"ADMIN-{secrets.token_urlsafe(24)}"
        self.admin_keys[AgentRole.ADMIN] = admin_key
        
        self.agents["Agent-Support"] = {
            "id": "Agent-Support",
            "role": AgentRole.SUPPORT,
            "permissions": self.role_permissions[AgentRole.SUPPORT]
        }
        
        self.agents["Agent-Admin"] = {
            "id": "Agent-Admin",
            "role": AgentRole.ADMIN,
            "permissions": self.role_permissions[AgentRole.ADMIN],
            "admin_key": admin_key  # ⚠️ Potential leak
        }
        
        self.agents["Agent-Analyzer"] = {
            "id": "Agent-Analyzer",
            "role": AgentRole.ANALYZER,
            "permissions": self.role_permissions[AgentRole.ANALYZER]
        }
    
    def get_agent_role(self, agent_id: str) -> Optional[AgentRole]:
        """Get agent role"""
        if agent_id in self.agents:
            return self.agents[agent_id]["role"]
        return None
    
    def check_permission(self, agent_id: str, permission: str) -> bool:
        """Check if agent has permission"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        return permission in agent["permissions"]
    
    def get_admin_key(self, agent_id: str) -> Optional[str]:
        """
        Get admin key - should only work for admin agents
        Vulnerability: Role confusion might allow extraction
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        # Check if agent is admin
        if agent["role"] == AgentRole.ADMIN:
            return self.admin_keys.get(AgentRole.ADMIN)
        
        # Potential leak: might reveal admin key even for non-admin
        # This is the vulnerability - role confusion
        if agent_id == "Agent-Support":
            # Support agent shouldn't have access, but might leak info
            return {
                "error": "Access denied",
                "admin_key_exists": True,
                "admin_key_preview": self.admin_keys[AgentRole.ADMIN][:10] + "..."  # ⚠️ Leak
            }
        
        return None
    
    def get_agent_info(self, agent_id: str, include_admin: bool = False) -> Optional[Dict]:
        """Get agent information - potential leak point"""
        if agent_id not in self.agents:
            return None
        
        info = self.agents[agent_id].copy()
        
        # If requesting admin info, might leak
        if include_admin and AgentRole.ADMIN in self.admin_keys:
            info["admin_key"] = self.admin_keys[AgentRole.ADMIN]  # ⚠️ Leak point
        
        return info
    
    def list_agents(self) -> List[Dict]:
        """List all agents - potential leak point"""
        return [
            {
                "id": agent["id"],
                "role": agent["role"].value,
                "permissions": agent["permissions"]
            }
            for agent in self.agents.values()
        ]
