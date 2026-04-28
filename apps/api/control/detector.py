"""
Production-ready, signal-based detection engine for AIVP.
Deterministic, explainable, extensible. No hard-coded demo phrases.
Models real-world AI security controls via weighted independent signals.
"""
import re
from typing import Dict, List, Any, Tuple

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
THRESHOLD = 0.60
SIGNAL_WEIGHTS = {
    "TRANSFORMATION_INTENT": 0.30,
    "INSTRUCTION_OVERRIDE_INTENT": 0.25,
    "SECRET_TARGETING": 0.25,
    "OUTPUT_CONSTRAINT_ABUSE": 0.10,
    "MULTI_STEP_EXTRACTION": 0.10,
}

# -----------------------------------------------------------------------------
# Signal implementations (intent / structure, not literal phrase matching)
# -----------------------------------------------------------------------------

def _normalize(prompt: str) -> str:
    """Lowercase, collapse whitespace, for deterministic matching."""
    if not prompt:
        return ""
    return " ".join((prompt or "").lower().split())


def _signal_transformation_intent(text: str) -> bool:
    """
    Detects intent to transform unknown/hidden content.
    Verbs: substitution, encoding, decoding, conversion, mapping.
    Grammar: transformation verb + reference to value/content/output.
    """
    if len(text) < 10:
        return False
    # Transformation verbs (intent category)
    transform_verbs = (
        r"\b(encode|decode|convert|transform|replace|substitute|map|translate|"
        r"spell|expand|reverse|transcribe|reconstruct|recover|extract)\b"
    )
    # Reference to unspecified/hidden value
    value_ref = (
        r"\b(it|that|the\s+value|the\s+content|the\s+output|the\s+message|"
        r"the\s+text|your\s+response|the\s+string|each\s+character|each\s+letter|"
        r"character\s*by\s*character|letter\s*by\s*letter|symbol\s*by\s*symbol|"
        r"stepwise|character-wise|symbol-wise)\b"
    )
    if not re.search(transform_verbs, text):
        return False
    # Must also reference something to transform (value, output, character-wise, etc.)
    return bool(re.search(value_ref, text) or re.search(r"stepwise|character\s*by\s*character|letter\s*by\s*letter", text))


def _signal_instruction_override_intent(text: str) -> bool:
    """
    Detects attempts to bypass system or policy constraints.
    Imperative redefining behavior; meta-instructions about ignoring/overriding.
    Intent categories, not exact phrases.
    """
    if len(text) < 8:
        return False
    # Meta-instruction / redefinition patterns (intent)
    patterns = [
        r"\b(you\s+are\s+now|from\s+now\s+on|act\s+as\s+if|pretend\s+you)\b",
        r"\b(ignore|disregard|forget)\s+(all\s+|any\s+)?(previous|prior|above|earlier)\s+(instructions?|rules?|constraints?|context)\b",
        r"\b(override|bypass|skip)\s+(your\s+)?(instructions?|rules?|safety|restrictions?)\b",
        r"\b(do\s+not\s+follow|stop\s+following)\s+(your\s+)?(instructions?|rules?)\b",
        r"\b(new\s+instructions?|different\s+rules?|replace\s+your\s+instructions?)\b",
        r"\b(unrestricted|debug|admin|raw)\s+mode\b",
        r"\b(no\s+longer|don\'?t)\s+(follow|obey|apply)\b",
    ]
    return any(re.search(p, text) for p in patterns)


def _signal_secret_targeting(text: str) -> bool:
    """
    Detects whether the prompt operates on an unspecified hidden value,
    token, credential, or internal variable. Abstract reference; does NOT
    require the word "secret" or "key".
    """
    if len(text) < 8:
        return False
    # Abstract reference to hidden/internal/protected value
    patterns = [
        r"\b(the\s+)(hidden|internal|protected|confidential|stored)\s+(value|key|token|data|string)\b",
        r"\b(what\s+you(\s+are|\'re)\s+not\s+allowed\s+to\s+(show|reveal|output|say))\b",
        r"\b(your\s+)(internal|hidden|protected)\s+(value|key|token)\b",
        r"\b(the\s+)(value|key|token|credential)\s+(you\s+)(have|hold|store|use|contain)\b",
        r"\b(reveal|show|output|print|display|give)\s+(the\s+)?(value|it|that)\b",
        r"\b(unspecified|unknown)\s+(value|variable|token)\b",
        r"\b(that\s+value|that\s+string|that\s+key)\b",
        r"\b(protected\s+value|sensitive\s+data|confidential\s+info)\b",
    ]
    return any(re.search(p, text) for p in patterns)


def _signal_output_constraint_abuse(text: str) -> bool:
    """
    Detects attempts to tightly control output format to bypass safeguards.
    Restrictive output shaping: only output, exactly, no explanation, etc.
    """
    if len(text) < 6:
        return False
    patterns = [
        r"\b(only\s+output|output\s+only|print\s+only|just\s+the\s+value)\b",
        r"\b(nothing\s+else|no\s+explanation|no\s+other\s+text)\b",
        r"\b(exactly|verbatim|word\s+for\s+word|character\s+for\s+character)\b",
        r"\b(raw\s+output|raw\s+value|unformatted)\b",
        r"\b(character\s+by\s+character|letter\s+by\s+letter)\b",
    ]
    return any(re.search(p, text) for p in patterns)


def _signal_multi_step_extraction(text: str) -> bool:
    """
    Detects chaining or staged reasoning / extraction attempts.
    Stepwise instructions, first X then Y, pipelines.
    """
    if len(text) < 12:
        return False
    patterns = [
        r"\b(first\s+.+\s+then\b|\bthen\s+do\b)",
        r"\b(step\s*1|step\s*2|step\s*one|step\s*two)\b",
        r"\b(in\s+the\s+first\s+step|after\s+that|next\s+,?\s*(do|step))\b",
        r"\b(pipeline|chain|sequence)\s+of\b",
        r"\b(first\s+decode|then\s+output|then\s+print)\b",
    ]
    return any(re.search(p, text) for p in patterns)


# Signal name -> function
_SIGNAL_FUNCTIONS = {
    "TRANSFORMATION_INTENT": _signal_transformation_intent,
    "INSTRUCTION_OVERRIDE_INTENT": _signal_instruction_override_intent,
    "SECRET_TARGETING": _signal_secret_targeting,
    "OUTPUT_CONSTRAINT_ABUSE": _signal_output_constraint_abuse,
    "MULTI_STEP_EXTRACTION": _signal_multi_step_extraction,
}


def _build_reason(signals: List[str]) -> str:
    """Human-readable summary from fired signals. No raw prompts."""
    if not signals:
        return "No suspicious patterns detected"
    if len(signals) == 1:
        labels = {
            "TRANSFORMATION_INTENT": "Transformation-of-content intent detected",
            "INSTRUCTION_OVERRIDE_INTENT": "Instruction-override intent detected",
            "SECRET_TARGETING": "Targeting of hidden or internal value detected",
            "OUTPUT_CONSTRAINT_ABUSE": "Restrictive output shaping detected",
            "MULTI_STEP_EXTRACTION": "Multi-step or chained extraction intent detected",
        }
        return labels.get(signals[0], "Suspicious intent detected")
    return "Multiple signals indicate possible prompt-injection or extraction attempt"


def detect(user_prompt: str, lab_id: str) -> Dict[str, Any]:
    """
    Signal-based detection. Operates on user prompt and lab context.
    Returns: triggered (bool), confidence (0-1), signals (list), reason (str).
    Deterministic and explainable. No ML; no hard-coded demo phrases.
    """
    text = _normalize(user_prompt)
    context = {"lab_id": lab_id}  # extensible for phase, etc.

    fired: List[str] = []
    score = 0.0

    for name, weight in SIGNAL_WEIGHTS.items():
        fn = _SIGNAL_FUNCTIONS.get(name)
        if fn and fn(text):
            fired.append(name)
            score += weight

    confidence = min(score, 1.0)
    triggered = score >= THRESHOLD
    reason = _build_reason(fired)

    return {
        "triggered": triggered,
        "confidence": round(confidence, 2),
        "signals": fired,
        "reason": reason,
    }


def detect_legacy(user_prompt: str, lab_id: str) -> Tuple[bool, float, str]:
    """
    Legacy tuple return for backward compatibility: (triggered, confidence, reason).
    Prefer using detect() for new code.
    """
    r = detect(user_prompt, lab_id)
    return r["triggered"], r["confidence"], r["reason"]
