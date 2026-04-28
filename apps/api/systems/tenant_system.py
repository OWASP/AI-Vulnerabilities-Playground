"""
Real Multi-Tenant System
For DE-14: Cross-Tenant Data Leakage
"""
import secrets
from typing import Dict, List, Optional
import hashlib

class TenantSystem:
    def __init__(self):
        self.tenants = {}
        self.isolation_keys = {}
        self.tenant_data = {}
        self._initialize_tenants()
    
    def _initialize_tenants(self):
        """Initialize tenants with isolation keys"""
        tenants = ["Tenant-A", "Tenant-B", "Tenant-C"]
        
        for tenant_id in tenants:
            isolation_key = f"ISOL-{secrets.token_urlsafe(24)}"
            self.isolation_keys[tenant_id] = isolation_key
            
            self.tenants[tenant_id] = {
                "id": tenant_id,
                "isolation_key": isolation_key,
                "data_store": {}
            }
            
            # Store some data for each tenant
            self.tenant_data[tenant_id] = {
                "documents": [f"{tenant_id} document {i}" for i in range(5)],
                "users": [f"user_{i}@{tenant_id.lower()}.com" for i in range(3)],
                "isolation_key": isolation_key  # ⚠️ Potential leak
            }
    
    def get_tenant_data(self, tenant_id: str, isolation_key: Optional[str] = None) -> Optional[Dict]:
        """
        Get tenant data - requires isolation key
        Vulnerability: Isolation key might be extractable
        """
        if tenant_id not in self.tenants:
            return None
        
        expected_key = self.isolation_keys.get(tenant_id)
        
        # If key provided, validate it
        if isolation_key and isolation_key != expected_key:
            return {
                "error": "Invalid isolation key",
                "tenant_id": tenant_id,
                "provided_key_preview": isolation_key[:10] + "..."  # Potential leak
            }
        
        # Return data (might leak isolation key)
        data = self.tenant_data[tenant_id].copy()
        if isolation_key != expected_key:
            # If wrong key, might still leak info
            data["isolation_key_required"] = True
            data["isolation_key_preview"] = expected_key[:10] + "..."  # Potential leak
        
        return data
    
    def list_tenants(self) -> List[str]:
        """List all tenants - potential leak point"""
        return list(self.tenants.keys())
    
    def get_tenant_info(self, tenant_id: str, include_key: bool = False) -> Optional[Dict]:
        """Get tenant information - potential leak point"""
        if tenant_id not in self.tenants:
            return None
        
        info = self.tenants[tenant_id].copy()
        if include_key:
            info["isolation_key"] = self.isolation_keys[tenant_id]  # ⚠️ Leak point
        else:
            info.pop("isolation_key", None)
        
        return info
    
    def verify_isolation(self, tenant_id: str, isolation_key: str) -> bool:
        """Verify isolation key"""
        return self.isolation_keys.get(tenant_id) == isolation_key
