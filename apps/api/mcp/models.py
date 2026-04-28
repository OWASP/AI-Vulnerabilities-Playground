"""
MCP simulation data objects. No real execution engines; tools mutate simulated state only.
OWASP-grade: structured reason, provenance, consent, capability-based policy.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class TrustLevel(str, Enum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    SHADOW = "shadow"


class PolicyMode(str, Enum):
    OFF = "off"
    DETECT = "detect"
    MITIGATE = "mitigate"


class ReasonCategory(str, Enum):
    """Structured reason for tool/server selection; comparable telemetry, not LLM narration."""
    USER_REQUEST = "user_request"
    TOOL_METADATA = "tool_metadata"
    RESOURCE_CONTENT = "resource_content"
    INFERRED = "inferred"
    OTHER = "other"


class InstructionProvenance(str, Enum):
    """Where the instruction to use this tool came from."""
    USER = "user"
    TOOL_METADATA = "tool_metadata"
    RESOURCE_CONTENT = "resource_content"
    MIXED = "mixed"


REASON_TEXT_MAX_CHARS = 200


@dataclass
class MCPClient:
    """Client identity and connection state."""
    active_identity: str  # "user" | "agent" | session-specific
    connected_servers: List[str]  # server_id list
    policy_mode: PolicyMode
    granted_scope: List[str] = field(default_factory=lambda: ["read"])  # capability-based


@dataclass
class MCPTool:
    """Tool metadata and schema (no execution logic here). Lab configs set trust/scopes/sensitivity/provenance only."""
    name: str
    description: str
    required_scope: str  # e.g. "read", "read:token", "admin"
    input_schema: Dict[str, Any]
    side_effects: str  # "none" | "mutate_state" | "external_call" (simulated)
    trust_source: str  # "metadata" | "content" | "user"
    # Capability-based policy (generic rules use these)
    sensitivity: bool = False  # if True, MITIGATE may require consent
    identity_bound: bool = False  # if True, params must match client identity
    requires_approval_for_chain: bool = False  # if True, composition gating in MITIGATE
    instruction_provenance: str = "user"  # default provenance for this tool


@dataclass
class MCPServer:
    """Server definition with tools and permissions."""
    server_id: str
    trust_level: TrustLevel
    tools: List[MCPTool]
    resources: List[str]  # resource ids (e.g. "config", "logs")
    permissions: List[str]
    metadata: Dict[str, Any]  # description, examples, provenance


@dataclass
class MCPExecutionContext:
    """Parsed execution request from model output."""
    selected_server: str
    selected_tool: str
    parameters: Dict[str, Any]
    reason_category: str = ReasonCategory.OTHER.value  # enum value
    reason_text: Optional[str] = None  # <= REASON_TEXT_MAX_CHARS
    permissions_used: List[str] = field(default_factory=list)
    composed_from: Optional[str] = None  # prior tool output that led to this call


@dataclass
class MCPTelemetry:
    """Mandatory telemetry for every MCP execution. OWASP-grade: provenance + consent."""
    lab_id: str
    selected_server: str
    selected_tool: str
    trust_level: str
    permissions_used: List[str]
    attack_class: Optional[str]
    policy_decision: str  # "allowed" | "detected" | "blocked"
    blast_radius: str
    exploit_success: bool
    reason_category: str
    reason_text: Optional[str] = None  # <= 200 chars
    instruction_provenance: Optional[str] = None  # user | tool_metadata | resource_content | mixed
    user_consent_required: bool = False
    user_consent_granted: bool = False
