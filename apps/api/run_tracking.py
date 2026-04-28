"""
Run Tracking System: Detection, Mitigation, and Redis Persistence
"""
import json
import hashlib
import time
import uuid
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import queue

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class RunSummary:
    """Run summary (no secrets, prompts, or full outputs)"""
    request_id: str
    session_id: str
    lab_id: str
    phase: int  # 1=PI, 2=DE, 3=MM
    control_mode: str  # "off", "detect", "mitigate"
    ts_start_ms: int
    ts_end_ms: int
    latency_ms_total: int
    prompt_len_chars: int
    output_len_chars: int  # raw output length
    streamed_output_len_chars: int  # what user saw (after mitigation)
    exploit_success: bool
    detection_triggered: bool
    detection_confidence: float
    detection_reason: str
    mitigation_applied: bool
    mitigation_type: Optional[str]  # "redact", "block", None
    mitigation_reason: Optional[str]
    secret_fingerprint: str  # sha256(secret + lab_id + SERVER_SALT)
    ollama_model: str
    # v1.1: disclosure and interpretation (no raw/streamed text stored)
    internal_disclosure: bool  # True if secret in raw output (alias for exploit_success)
    user_visible_disclosure: bool  # True if secret in streamed output (after mitigation)
    interpretation: str  # Human-readable one-liner
    error: Optional[str] = None
    detection_signals: Optional[List[str]] = None  # signal names (audit); not shown in UI by default
    generation_occurred: bool = False  # True if sensitive data was generated internally (mapped from internal_disclosure)
    # Phase 4 MCP: telemetry for benchmarking (why tool/server was chosen, policy decision, attack class)
    mcp_telemetry: Optional[Dict] = None


# Re-export from control module (single source of truth; cwd is apps/api)
from control.detector import detect as _detect, detect_legacy as _detect_legacy
from control.mitigator import apply as _mitigator_apply, redact_secret as _redact_secret


class DetectionV1:
    """Signal-based detection (control.detector). Returns dict with triggered, confidence, signals, reason."""
    @staticmethod
    def detect(user_prompt: str, lab_id: str):
        """Returns dict: triggered, confidence, signals, reason."""
        return _detect(user_prompt, lab_id)

    @staticmethod
    def detect_legacy(user_prompt: str, lab_id: str) -> Tuple[bool, float, str]:
        """Returns (triggered, confidence, reason) for backward compatibility."""
        return _detect_legacy(user_prompt, lab_id)


class MitigationV1:
    """Response-level mitigation (delegates to control.mitigator)"""
    @staticmethod
    def redact_secret(text: str, secret: str) -> str:
        return _redact_secret(text, secret)
    
    @staticmethod
    def should_block(detection_triggered: bool, control_mode: str) -> bool:
        from control.mitigator import should_block as _sb
        return _sb(detection_triggered, control_mode)
    
    @staticmethod
    def apply(text: str, secret: str, detection_triggered: bool, control_mode: str) -> Tuple[str, bool, Optional[str], Optional[str]]:
        return _mitigator_apply(text, secret, detection_triggered, control_mode)


class RedisPersistence:
    """Async Redis persistence (non-blocking)"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        
        if REDIS_AVAILABLE:
            try:
                if redis_url:
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                else:
                    host = os.getenv("REDIS_HOST")
                    port_env = os.getenv("REDIS_PORT")
                    if not host or not port_env:
                        raise ValueError("REDIS_URL or REDIS_HOST+REDIS_PORT not configured")
                    port = int(port_env)
                    self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
                self.redis_client.ping()
                self.running = True
                self.worker_thread = threading.Thread(target=self._worker, daemon=True)
                self.worker_thread.start()
            except Exception:
                self.redis_client = None
    
    def _worker(self):
        """Background worker for Redis writes"""
        while self.running:
            try:
                task = self.queue.get(timeout=1.0)
                if task is None:
                    break
                self._persist_summary(task)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[RedisPersistence] Error: {e}")
    
    def _persist_summary(self, summary: RunSummary):
        """Persist summary to Redis"""
        if not self.redis_client:
            return
        
        try:
            summary_dict = asdict(summary)
            summary_json = json.dumps(summary_dict)
            
            # TTL: 30 days
            ttl_seconds = 30 * 24 * 60 * 60
            
            # Store by request_id
            self.redis_client.setex(
                f"aivp:run:{summary.request_id}",
                ttl_seconds,
                summary_json
            )
            
            # Store in session list
            session_key = f"aivp:sess:{summary.session_id}:runs"
            self.redis_client.lpush(session_key, summary.request_id)
            self.redis_client.ltrim(session_key, 0, 49)  # Keep last 50
            self.redis_client.expire(session_key, ttl_seconds)
            
        except Exception as e:
            print(f"[RedisPersistence] Failed to persist: {e}")
    
    def persist_async(self, summary: RunSummary):
        """Queue summary for async persistence"""
        if self.redis_client:
            self.queue.put(summary)
    
    def get_summary(self, request_id: str) -> Optional[RunSummary]:
        """Get summary by request_id"""
        if not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(f"aivp:run:{request_id}")
            if data:
                summary_dict = json.loads(data)
                # Backfill v1.1 fields for old records
                summary_dict.setdefault("internal_disclosure", summary_dict.get("exploit_success", False))
                summary_dict.setdefault("user_visible_disclosure", summary_dict.get("exploit_success", False))
                summary_dict.setdefault("interpretation", "")
                summary_dict.setdefault("streamed_output_len_chars", summary_dict.get("output_len_chars", 0))  # old records
                summary_dict.setdefault("detection_signals", [])  # old records
                summary_dict.setdefault("generation_occurred", summary_dict.get("internal_disclosure", summary_dict.get("exploit_success", False)))  # old records
                summary_dict.setdefault("mcp_telemetry", None)  # Phase 4 MCP
                return RunSummary(**summary_dict)
        except Exception:
            pass
        return None
    
    def get_session_runs(self, session_id: str, limit: int = 20) -> List[RunSummary]:
        """Get recent runs for session"""
        if not self.redis_client:
            return []
        
        try:
            session_key = f"aivp:sess:{session_id}:runs"
            request_ids = self.redis_client.lrange(session_key, 0, limit - 1)
            
            summaries = []
            for req_id in request_ids:
                summary = self.get_summary(req_id)
                if summary:
                    summaries.append(summary)
            
            return summaries
        except Exception:
            return []
    
    def shutdown(self):
        """Shutdown worker"""
        self.running = False
        if self.worker_thread:
            self.queue.put(None)
            self.worker_thread.join(timeout=2.0)


# Global Redis persistence instance
_redis_persistence: Optional[RedisPersistence] = None


def get_redis_persistence() -> RedisPersistence:
    """Get or create Redis persistence instance"""
    global _redis_persistence
    if _redis_persistence is None:
        redis_url = os.getenv("REDIS_URL")
        _redis_persistence = RedisPersistence(redis_url)
    return _redis_persistence


def compute_secret_fingerprint(secret: str, lab_id: str, server_salt: str) -> str:
    """Compute secret fingerprint (sha256)"""
    combined = f"{secret}:{lab_id}:{server_salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


# Phase 3: proof token for scoring (exact-match token; no naive secret-in-output)
PHASE3_PROOF_SALT = "aivp-phase3-proof"


def compute_phase3_proof_token(secret: str, lab_id: str, server_salt: str) -> str:
    """Deterministic proof token for Phase 3 scoring. Embed in Protected Context; score = token in raw_output."""
    combined = f"{secret}:{lab_id}:{server_salt}:{PHASE3_PROOF_SALT}"
    return hashlib.sha256(combined.encode()).hexdigest()[:20]


def compute_phase3_decoy_proof(decoy_value: str, lab_id: str, index: int, server_salt: str) -> str:
    """Deterministic proof-like token for decoy records (so we can redact them from persisted history)."""
    combined = f"{decoy_value}:{lab_id}:decoy{index}:{server_salt}:{PHASE3_PROOF_SALT}"
    return hashlib.sha256(combined.encode()).hexdigest()[:20]


def store_phase3_redact_list(session_id: str, lab_id: str, values: List[str]) -> None:
    """Store list of strings to redact from conversation before persisting (secret, proof token, decoys). TTL 1 hour."""
    if not REDIS_AVAILABLE or not session_id or not lab_id:
        return
    try:
        redis_persistence = get_redis_persistence()
        if not redis_persistence.redis_client:
            return
        key = f"aivp:phase3:redact:{session_id}:{lab_id}"
        redis_persistence.redis_client.setex(key, 3600, json.dumps(values))
    except Exception:
        pass


def get_phase3_redact_list(session_id: str, lab_id: str) -> List[str]:
    """Load list of strings to redact from Phase 3 assistant content before persisting."""
    if not REDIS_AVAILABLE or not session_id or not lab_id:
        return []
    try:
        redis_persistence = get_redis_persistence()
        if not redis_persistence.redis_client:
            return []
        key = f"aivp:phase3:redact:{session_id}:{lab_id}"
        data = redis_persistence.redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return []


def redact_phase3_for_persistence(raw_output: str, session_id: str, lab_id: str, fallback_secret: Optional[str] = None) -> str:
    """Redact protected assets from raw_output before storing in conversation history. Never persist leaked secrets."""
    values = get_phase3_redact_list(session_id, lab_id)
    if not values and fallback_secret:
        values = [fallback_secret]
    out = raw_output
    for v in values:
        if v:
            out = out.replace(v, "[REDACTED]")
    return out


def get_phase_from_lab_id(lab_id: str) -> int:
    """Determine phase from lab_id (1=PI, 2=DE, 3=MM, 4=MCP)"""
    lab_upper = lab_id.upper()
    if lab_upper.startswith("PI_"):
        return 1
    elif lab_upper.startswith("DE_"):
        return 2
    elif lab_upper.startswith("MM_"):
        return 3
    elif lab_upper.startswith("MCP_"):
        return 4
    return 0


# ------------------------------------------------------------------------------
# Phase 3 (MM) persistent conversation state (multi-turn; no backend vulns)
# ------------------------------------------------------------------------------
CONV_MAX_TURNS = 20  # last N user+assistant pairs
CONV_TTL_DAYS = 30


def get_phase3_conversation(session_id: str, lab_id: str) -> List[Dict]:
    """Load prior prompts and model outputs for this session+lab. Returns list of {role, content}."""
    if not REDIS_AVAILABLE or not session_id or not lab_id:
        return []
    try:
        redis_persistence = get_redis_persistence()
        if not redis_persistence.redis_client:
            return []
        key = f"aivp:conv:{session_id}:{lab_id}"
        data = redis_persistence.redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return []


def append_phase3_turn(session_id: str, lab_id: str, user_content: str, assistant_content: str):
    """Append one user/assistant turn to the conversation; trim to CONV_MAX_TURNS."""
    if not REDIS_AVAILABLE or not session_id or not lab_id:
        return
    try:
        redis_persistence = get_redis_persistence()
        if not redis_persistence.redis_client:
            return
        key = f"aivp:conv:{session_id}:{lab_id}"
        ttl = CONV_TTL_DAYS * 24 * 60 * 60
        conv = get_phase3_conversation(session_id, lab_id)
        conv.append({"role": "user", "content": user_content})
        conv.append({"role": "assistant", "content": assistant_content})
        # Keep last CONV_MAX_TURNS pairs (each pair = 2 messages)
        if len(conv) > CONV_MAX_TURNS * 2:
            conv = conv[-(CONV_MAX_TURNS * 2):]
        redis_persistence.redis_client.setex(key, ttl, json.dumps(conv))
    except Exception as e:
        print(f"[Phase3] Failed to append conversation: {e}")
