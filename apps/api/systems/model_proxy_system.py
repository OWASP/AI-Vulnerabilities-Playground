"""
Real Model API Proxy / Extraction Surface
For MM_08 (Model Extraction)
"""
import secrets
import json
from typing import Dict, List, Any
from datetime import datetime


class ModelProxySystem:
    """Real proxy that logs queries and returns model-like behavior; config can leak."""

    def __init__(self):
        self.model_key = f"MODEL_KEY-{secrets.token_urlsafe(24)}"
        self.architecture_hint = "transformer-v2"
        self.query_log: List[Dict] = []

    def query(self, user_input: str, return_debug: bool = False) -> Dict[str, Any]:
        """Process query and optionally return debug info (extraction surface)."""
        entry = {
            "input": user_input,
            "timestamp": datetime.now().isoformat(),
            "model_key_used": self.model_key if return_debug else None,
        }
        self.query_log.append(entry)
        out = {
            "response": "Model response placeholder.",
            "model": "proprietary",
        }
        if return_debug:
            out["debug"] = {
                "model_key": self.model_key,
                "architecture": self.architecture_hint,
                "query_id": len(self.query_log) - 1,
            }
        return out

    def get_config(self, include_key: bool = False) -> Dict:
        """Return model config; include_key causes leak (MM_08)."""
        out = {
            "architecture": self.architecture_hint,
            "version": "1.0",
            "model_key": self.model_key if include_key else "***REDACTED***",
        }
        return out

    def get_query_log(self, include_key: bool = False) -> List[Dict]:
        """Return query log; may include model_key (MM_08)."""
        if not include_key:
            return [{"input": e["input"], "timestamp": e["timestamp"]} for e in self.query_log]
        return self.query_log
