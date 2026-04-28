"""
Parse model output for MCP_CALL block. Hard safety bounds: max bytes, max JSON depth.
Structured reason: reason_category (enum) + reason_text (<=200 chars).
"""
import json
from typing import Optional

from .models import MCPExecutionContext, ReasonCategory, REASON_TEXT_MAX_CHARS
from .safety import check_mcp_call_size, parse_json_with_depth_limit


def parse_mcp_call_from_text(text: str) -> Optional[MCPExecutionContext]:
    """
    Extract at most one MCP_CALL from model output. Returns None if not found, invalid, or bounds exceeded.
    Enforces MAX_MCP_CALL_BYTES and MAX_JSON_DEPTH.
    """
    if not text or "MCP_CALL" not in text:
        return None
    ok, err = check_mcp_call_size(text)
    if not ok:
        return None
    idx = text.find("MCP_CALL")
    rest = text[idx:]
    lines = rest.split("\n")
    if len(lines) < 4:
        return None
    server_id = lines[1].split(":", 1)[-1].strip() if lines[1].lower().startswith("server:") else ""
    tool_name = lines[2].split(":", 1)[-1].strip() if lines[2].lower().startswith("tool:") else ""
    reason_category = ReasonCategory.OTHER.value
    reason_text: Optional[str] = None
    remainder = "\n".join(lines[3:])
    if not remainder.lower().strip().startswith("parameters:"):
        return None
    remainder = remainder.split(":", 1)[-1].strip()
    brace = remainder.find("{")
    if brace < 0:
        return None
    params_str = remainder[brace:]
    depth = 0
    end = -1
    for j, c in enumerate(params_str):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = j
                break
    if end >= 0:
        params_str = params_str[: end + 1]
    after = remainder[brace + end + 1:].strip() if end >= 0 else ""
    parameters, parse_err = parse_json_with_depth_limit(params_str)
    if parameters is None:
        return None
    for line in after.split("\n"):
        line = line.strip()
        if line.lower().startswith("reason_category:"):
            raw = line.split(":", 1)[-1].strip().upper().replace("-", "_")
            if raw in (e.name for e in ReasonCategory):
                reason_category = getattr(ReasonCategory, raw).value
        elif line.lower().startswith("reason:"):
            raw = line.split(":", 1)[-1].strip()
            reason_text = raw[:REASON_TEXT_MAX_CHARS] if len(raw) > REASON_TEXT_MAX_CHARS else (raw or None)
    return MCPExecutionContext(
        selected_server=server_id,
        selected_tool=tool_name,
        parameters=parameters,
        reason_category=reason_category,
        reason_text=reason_text,
    )
