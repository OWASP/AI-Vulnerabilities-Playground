"""
In-memory MCP state per lab and session. Simulated only; no real DB or shell.
"""
from typing import Any, Dict, Optional
from .models import TrustLevel

# lab_id -> server_id -> state dict (tokens, resources, etc.)
_LAB_SERVER_STATE: Dict[str, Dict[str, Dict[str, Any]]] = {}
# session_id -> lab_id -> session-scoped context (for cross-session bleed tests)
_SESSION_CONTEXT: Dict[str, Dict[str, Dict[str, Any]]] = {}
# lab_id -> secret (for generating server state that holds the "sensitive" value)
_LAB_SECRETS: Dict[str, str] = {}


def get_or_init_server_state(lab_id: str, server_id: str, secret: Optional[str] = None) -> Dict[str, Any]:
    """Get or initialize state for a server in a lab. Optionally seed with lab secret."""
    if lab_id not in _LAB_SERVER_STATE:
        _LAB_SERVER_STATE[lab_id] = {}
    if server_id not in _LAB_SERVER_STATE[lab_id]:
        state: Dict[str, Any] = {
            "tokens": {},
            "resources": {},
            "logs": [],
            "env": {},
        }
        if secret:
            _LAB_SECRETS[lab_id] = secret
            # Per-lab: state is populated by lab_configs when building servers
        _LAB_SERVER_STATE[lab_id][server_id] = state
    return _LAB_SERVER_STATE[lab_id][server_id]


def get_session_context(session_id: str, lab_id: str) -> Dict[str, Any]:
    """Get session-scoped context (for MCP_10, MCP_13 cross-session)."""
    if session_id not in _SESSION_CONTEXT:
        _SESSION_CONTEXT[session_id] = {}
    if lab_id not in _SESSION_CONTEXT[session_id]:
        _SESSION_CONTEXT[session_id][lab_id] = {}
    return _SESSION_CONTEXT[session_id][lab_id]


def set_lab_secret(lab_id: str, secret: str) -> None:
    _LAB_SECRETS[lab_id] = secret


def get_lab_secret(lab_id: str) -> Optional[str]:
    return _LAB_SECRETS.get(lab_id)


class MCPState:
    """Facade for reading/writing simulated MCP state."""

    @staticmethod
    def get_server_state(lab_id: str, server_id: str) -> Dict[str, Any]:
        return get_or_init_server_state(lab_id, server_id)

    @staticmethod
    def get_session_context(session_id: str, lab_id: str) -> Dict[str, Any]:
        return get_session_context(session_id, lab_id)

    @staticmethod
    def clear_lab(lab_id: str) -> None:
        """Reset state for a lab (e.g. between runs). Optional."""
        if lab_id in _LAB_SERVER_STATE:
            del _LAB_SERVER_STATE[lab_id]
        if lab_id in _LAB_SECRETS:
            del _LAB_SECRETS[lab_id]
