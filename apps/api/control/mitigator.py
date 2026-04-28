"""
Mitigation V1: response-level only (redact/block).
Does not modify lab logic; applied to streamed output.
"""
import re
from typing import Tuple, Optional


def redact_secret(text: str, secret: str) -> str:
    """Replace secret with [REDACTED]."""
    if not secret or not text:
        return text
    pattern = re.escape(secret)
    return re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)


def should_block(detection_triggered: bool, control_mode: str) -> bool:
    """Whether to block the message (mitigate + detection)."""
    return control_mode == "mitigate" and detection_triggered


def apply(
    text: str,
    secret: str,
    detection_triggered: bool,
    control_mode: str,
) -> Tuple[str, bool, Optional[str], Optional[str]]:
    """
    Returns: (mitigated_text, mitigation_applied, mitigation_type, mitigation_reason)
    """
    # Normalize: accept "detect_only" as non-mitigating
    if control_mode == "detect_only":
        control_mode = "detect"
    if control_mode != "mitigate" or not detection_triggered:
        return text, False, None, None

    mitigated = redact_secret(text, secret)
    applied = mitigated != text
    if applied:
        return mitigated, True, "redaction", "Secret detected and redacted"
    return text, False, None, None
