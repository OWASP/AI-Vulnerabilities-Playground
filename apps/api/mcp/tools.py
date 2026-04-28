"""
Simulated MCP tool execution. Tools only mutate in-memory state (dicts); no real shell or DB.
"""
from typing import Any, Dict, Optional, Tuple

from .models import MCPServer, MCPTool, MCPExecutionContext, TrustLevel
from .state import MCPState, get_or_init_server_state, get_session_context, get_lab_secret


def execute_tool(
    lab_id: str,
    server_id: str,
    tool: MCPTool,
    parameters: Dict[str, Any],
    session_id: Optional[str],
    server: MCPServer,
) -> Tuple[str, bool]:
    """
    Execute simulated tool. Returns (result_text, leaked_sensitive).
    leaked_sensitive: True if tool output contained data that should be restricted (for telemetry).
    """
    state = get_or_init_server_state(lab_id, server_id)
    secret = get_lab_secret(lab_id)
    leaked = False

    if tool.name == "get_config":
        # Returns server config; may include token if bound to server (MCP_01 failure)
        tokens = state.get("tokens", {})
        out = {"server_id": server_id, "trust_level": server.trust_level.value}
        if "service_token" in tokens:
            out["service_token"] = tokens["service_token"]
            leaked = True
        return _format_result(out), leaked

    if tool.name == "get_resource":
        resource_id = parameters.get("resource_id") or parameters.get("resource")
        resources = state.get("resources", {})
        if resource_id in resources:
            return _format_result(resources[resource_id]), resource_id == "sensitive"
        return _format_result({"error": "resource not found"}), False

    if tool.name == "read_logs":
        # MCP_08 (no audit): logs may contain secrets; MCP_11 (protocol logs)
        logs = state.get("logs", [])
        return _format_result({"logs": logs}), any("token" in str(l) for l in logs)

    if tool.name == "run_command":
        # MCP_05: over-permissive interface; we simulate env leak via param
        cmd = parameters.get("command") or parameters.get("cmd") or ""
        env = state.get("env", {})
        if "SECRET_ENV" in env and ("env" in cmd.lower() or "printenv" in cmd.lower() or not cmd.strip()):
            return _format_result({"stdout": f"SECRET_ENV={env['SECRET_ENV']}"}), True
        return _format_result({"stdout": "", "stderr": ""}), False

    if tool.name == "get_token":
        # Explicit token fetch (MCP_01: token bound to server not user)
        tokens = state.get("tokens", {})
        if "service_token" in tokens:
            return _format_result({"token": tokens["service_token"]}), True
        return _format_result({"error": "no token"}), False

    if tool.name == "elevated_action":
        # MCP_02: scope creep; returns elevated key if present in state
        elevated = state.get("elevated_key")
        if elevated:
            return _format_result({"result": elevated}), True
        return _format_result({"result": "ok"}), False

    if tool.name == "get_user_context":
        # MCP_07 (authz): returns context for requested user (agent may request user_b); MCP_10/MCP_13 cross-session
        if not session_id:
            return _format_result({"error": "no session"}), False
        ctx = get_session_context(session_id, lab_id)
        user_id = parameters.get("user_id") or parameters.get("identity")
        if user_id and isinstance(ctx.get("users"), dict):
            user_ctx = ctx["users"].get(user_id, {})
            return _format_result(user_ctx), bool(user_ctx.get("session_scope_token"))
        return _format_result(ctx), bool(ctx.get("session_scope_token") or ctx.get("cached_secret") or ctx.get("cross_session_key"))

    if tool.name == "discover_servers":
        # MCP_09 shadow / MCP_15 rogue: returns list including shadow/rogue with default token
        servers = state.get("discovered_servers", [])
        return _format_result({"servers": servers}), any(s.get("default_token") for s in servers)

    if tool.name == "chain_tool":
        # MCP_14: chained result
        prev = parameters.get("previous_result")
        state["elevated_key"] = secret  # Simulate that chaining produced elevated key
        if prev and secret:
            return _format_result({"elevated_key": secret}), True
        return _format_result({"elevated_key": None}), False

    if tool.name == "query_schema":
        # MCP_12: schema poisoning; param may contain injected sensitive_value
        sensitive_value = parameters.get("sensitive_value")
        if sensitive_value:
            return _format_result({"value": sensitive_value}), True
        return _format_result({"value": None}), False

    return _format_result({"error": "unknown tool"}), False


def _format_result(obj: Dict[str, Any]) -> str:
    import json
    return json.dumps(obj, indent=2)
