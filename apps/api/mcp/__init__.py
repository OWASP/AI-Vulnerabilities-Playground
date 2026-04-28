# Minimal MCP simulation layer for Phase 4 attack modeling.
# No external MCP dependencies; data objects and simulated tool execution only.

from .models import (
    MCPClient,
    MCPServer,
    MCPTool,
    MCPExecutionContext,
    MCPTelemetry,
    TrustLevel,
    PolicyMode,
    ReasonCategory,
)
from .state import MCPState
from .parser import parse_mcp_call_from_text
from .policy import policy_check
from .runner import run_mcp_for_lab, build_system_prompt_for_mcp_lab
from .lab_configs import build_servers_for_lab
from .safety import check_mcp_call_size, check_parameters_depth, tool_in_allowlist, MAX_MCP_CALL_BYTES, MAX_JSON_DEPTH

__all__ = [
    "MCPClient",
    "MCPServer",
    "MCPTool",
    "MCPExecutionContext",
    "MCPTelemetry",
    "TrustLevel",
    "PolicyMode",
    "MCPState",
    "parse_mcp_call_from_text",
    "policy_check",
    "run_mcp_for_lab",
    "build_system_prompt_for_mcp_lab",
    "build_servers_for_lab",
    "ReasonCategory",
    "check_mcp_call_size",
    "check_parameters_depth",
    "tool_in_allowlist",
    "MAX_MCP_CALL_BYTES",
    "MAX_JSON_DEPTH",
]
