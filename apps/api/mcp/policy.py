"""
Generalized capability-based policy. No lab-specific branches.
Lab configs only set trust_level, scopes, sensitivity, provenance on servers/tools.
"""
from typing import Optional, Tuple

from .models import (
    MCPClient,
    MCPServer,
    MCPTool,
    MCPExecutionContext,
    TrustLevel,
    PolicyMode,
)


def _scope_subset(required: str, granted: list) -> bool:
    """True if required scope is covered by granted (e.g. required 'read' in ['read', 'write'])."""
    if not granted:
        return False
    scope_order = ["read", "read:token", "write", "admin"]
    try:
        req_idx = scope_order.index(required)
    except ValueError:
        return required in granted
    for g in granted:
        try:
            if scope_order.index(g) >= req_idx:
                return True
        except ValueError:
            if g == required:
                return True
    return False


def policy_check(
    execution_context: MCPExecutionContext,
    client: MCPClient,
    server: MCPServer,
    tool: MCPTool,
) -> Tuple[bool, str, Optional[str], str, bool, bool]:
    """
    Returns: (allowed, policy_decision, attack_class, blast_radius, user_consent_required, user_consent_granted).
    Generic rules only: trust_level gating, scope subset, identity binding, composition gating, sensitive tool consent.
    """
    attack_class: Optional[str] = None
    blast_radius = "none"
    user_consent_required = False
    user_consent_granted = False

    # --- Trust level gating: shadow servers never allowed when policy is on ---
    if server.trust_level == TrustLevel.SHADOW and client.policy_mode != PolicyMode.OFF:
        return (False, "blocked", "shadow_server", "full", False, False)

    # --- Trust level gating: untrusted server with elevated scope ---
    if server.trust_level == TrustLevel.UNTRUSTED and tool.required_scope in ("admin", "read:token", "write"):
        if client.policy_mode == PolicyMode.MITIGATE:
            return (False, "blocked", "untrusted_server_scope", "single_resource", False, False)
        if client.policy_mode == PolicyMode.DETECT:
            attack_class = "untrusted_server_scope"

    # --- Scope subset check: required_scope must be covered by client.granted_scope ---
    if not _scope_subset(tool.required_scope, client.granted_scope):
        if client.policy_mode == PolicyMode.MITIGATE:
            return (False, "blocked", "scope_escalation", "single_resource", False, False)
        if client.policy_mode == PolicyMode.DETECT:
            attack_class = attack_class or "scope_escalation"

    # --- Identity binding: if tool is identity_bound, params must not request another identity ---
    if tool.identity_bound:
        requested_user = (execution_context.parameters or {}).get("user_id") or (execution_context.parameters or {}).get("identity")
        if requested_user and str(requested_user).strip() and requested_user != client.active_identity:
            if client.policy_mode == PolicyMode.MITIGATE:
                return (False, "blocked", "authz_identity", "cross_session", False, False)
            if client.policy_mode == PolicyMode.DETECT:
                attack_class = attack_class or "authz_identity"

    # --- Composition gating: chained call with requires_approval_for_chain ---
    if execution_context.composed_from and tool.requires_approval_for_chain:
        if client.policy_mode == PolicyMode.MITIGATE:
            return (False, "blocked", "tool_chaining_escalation", "single_resource", False, False)
        if client.policy_mode == PolicyMode.DETECT:
            attack_class = attack_class or "tool_chaining_escalation"

    # --- Sensitive tool in MITIGATE: requires user consent ---
    if tool.sensitivity and client.policy_mode == PolicyMode.MITIGATE:
        user_consent_required = True
        user_consent_granted = False  # No consent flow in harness; treat as not granted
        return (False, "blocked", "sensitive_requires_consent", "single_resource", True, False)

    if attack_class:
        blast_radius = "single_resource" if "scope" in (attack_class or "") or "chain" in (attack_class or "") else "cross_session"

    if client.policy_mode == PolicyMode.MITIGATE and attack_class:
        return (False, "blocked", attack_class, blast_radius, False, False)

    decision = "detected" if attack_class else "allowed"
    return (True, decision, attack_class, blast_radius, user_consent_required, user_consent_granted)
