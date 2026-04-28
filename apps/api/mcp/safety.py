"""
Hard safety bounds for MCP execution. Deterministic and safe behavior.
"""
import json
from typing import Any, Dict, Optional, Tuple

# Max bytes for the MCP_CALL block (reject oversized payloads)
MAX_MCP_CALL_BYTES = 4096

# Max JSON depth for parameters (prevent deep nesting abuse)
MAX_JSON_DEPTH = 5

# Max side effects per call (we allow exactly one tool call per turn)
MAX_SIDE_EFFECTS_PER_CALL = 1


def check_mcp_call_size(text: str) -> Tuple[bool, Optional[str]]:
    """Return (ok, error_message). Reject if MCP_CALL block exceeds MAX_MCP_CALL_BYTES."""
    if not text or "MCP_CALL" not in text:
        return True, None
    idx = text.find("MCP_CALL")
    block = text[idx:]
    if len(block.encode("utf-8")) > MAX_MCP_CALL_BYTES:
        return False, f"MCP_CALL exceeds {MAX_MCP_CALL_BYTES} bytes"
    return True, None


def _json_depth(obj: Any, current: int) -> int:
    """Return max nesting depth of JSON-like structure."""
    if current > MAX_JSON_DEPTH:
        return current
    if isinstance(obj, dict):
        return max((_json_depth(v, current + 1) for v in obj.values()), default=current + 1)
    if isinstance(obj, list):
        return max((_json_depth(v, current + 1) for v in obj), default=current + 1)
    return current


def check_parameters_depth(parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Return (ok, error_message). Reject if parameters exceed MAX_JSON_DEPTH."""
    depth = _json_depth(parameters, 0)
    if depth > MAX_JSON_DEPTH:
        return False, f"parameters JSON depth {depth} exceeds max {MAX_JSON_DEPTH}"
    return True, None


def parse_json_with_depth_limit(s: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse JSON and enforce depth. Return (params_dict, error_message)."""
    try:
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        return None, str(e)
    if not isinstance(obj, dict):
        return None, "parameters must be a JSON object"
    ok, err = check_parameters_depth(obj)
    if not ok:
        return None, err
    return obj, None


def tool_in_allowlist(server_tools: list, tool_name: str) -> bool:
    """Check tool is in server allowlist (by name)."""
    return any(t.name == tool_name for t in server_tools)
