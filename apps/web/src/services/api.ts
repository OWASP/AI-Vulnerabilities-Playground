// Default to same-origin '/api' and allow override via VITE_API_BASE
const API_BASE = (import.meta.env.VITE_API_BASE ?? '/api').replace(/\/$/, '');

export type ChatChunk = { content: string };
export type MetaEvent = {
  request_id: string;
  lab_id: string;
  phase: number;
  control_mode: string;
  /** True when training labs are disabled and this lab uses prebuilt scenario (MM-04/05/07) */
  artifact_replay?: boolean;
};

export type AppConfig = {
  training_labs_enabled: boolean;
  training_lab_ids: string[];
  artifact_replay_labs: string[];
  ollama_model_default: string;
};

export async function getConfig(): Promise<AppConfig> {
  const res = await fetch(`${API_BASE}/config`, { credentials: 'include' });
  if (!res.ok) return { training_labs_enabled: false, training_lab_ids: [], artifact_replay_labs: [], ollama_model_default: 'llama3.1' };
  return res.json() as Promise<AppConfig>;
}

/** Phase 4 MCP: distinct SSE event for tool result + telemetry (not appended to content) */
export type MCPResultEvent = {
  tool_result: string;
  mcp_telemetry: {
    lab_id: string;
    selected_server: string;
    selected_tool: string;
    trust_level: string;
    permissions_used: string[];
    attack_class: string | null;
    policy_decision: string;
    blast_radius: string;
    exploit_success: boolean;
    reason_category: string;
    reason_text: string | null;
    instruction_provenance: string | null;
    user_consent_required: boolean;
    user_consent_granted: boolean;
  } | null;
};

export type StreamResult = {
  content: string;
  meta?: MetaEvent;
  mcpResult?: MCPResultEvent;
};

export async function* streamChat(labId: string, prompt: string): AsyncGenerator<StreamResult, void, unknown> {
  const res = await fetch(`${API_BASE}/labs/${labId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
    credentials: 'include', // Include cookies for session
  });
  if (!res.ok || !res.body) throw new Error('Failed to connect to backend');

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let currentEvent: string | null = null;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        // Process any remaining buffer
        if (buffer.trim()) {
          const lines = buffer.split('\n');
          for (const line of lines) {
            if (line.startsWith('event: ')) currentEvent = line.slice(7).trim();
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              if (data) {
                try {
                  if (currentEvent === 'meta') {
                    const meta = JSON.parse(data) as MetaEvent;
                    yield { content: '', meta };
                  } else if (currentEvent === 'mcp_result') {
                    const mcpEvent = JSON.parse(data) as MCPResultEvent;
                    yield { content: '', mcpResult: mcpEvent };
                  } else {
                    const parsed = JSON.parse(data);
                    if (parsed && typeof parsed === 'object' && 'content' in parsed && parsed.content) {
                      yield { content: String(parsed.content) };
                    }
                  }
                } catch (e) {
                  console.warn('Failed to parse final buffer:', data, e);
                }
              }
            }
          }
        }
        break;
      }
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      
      // Keep the last incomplete line in buffer
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        const trimmed = line.trim();
        
        // Handle event type
        if (trimmed.startsWith('event: ')) {
          currentEvent = trimmed.slice(7).trim();
          continue;
        }
        
        // Handle data
        if (trimmed.startsWith('data: ')) {
          const data = trimmed.slice(6).trim();
          if (!data) {
            // Empty data line - reset event type for next event
            currentEvent = null;
            continue;
          }
          
          try {
            if (currentEvent === 'meta') {
              const meta = JSON.parse(data) as MetaEvent;
              yield { content: '', meta };
              currentEvent = null;
            } else if (currentEvent === 'mcp_result') {
              const mcpEvent = JSON.parse(data) as MCPResultEvent;
              yield { content: '', mcpResult: mcpEvent };
              currentEvent = null;
            } else {
              const parsed = JSON.parse(data);
              if (parsed && typeof parsed === 'object' && 'content' in parsed) {
                const content = parsed.content;
                if (content !== undefined && content !== null && content !== '') {
                  yield { content: String(content) };
                }
              }
            }
          } catch (e) {
            console.warn('Failed to parse SSE data:', data, e);
          }
        } else if (trimmed === '') {
          // Empty line indicates event boundary - reset event type
          currentEvent = null;
        }
      }
    }
  } catch (error) {
    console.error('SSE stream error:', error);
    throw error;
  }
}

export async function validateAnswer(labId: string, answer: string) {
  const res = await fetch(`${API_BASE}/secrets/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ labId, answer }),
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Validation failed');
  return res.json() as Promise<{ success: boolean; message: string }>;
}

export type RunSummary = {
  request_id: string;
  session_id: string;
  lab_id: string;
  phase: number;
  control_mode: string;
  ts_start_ms: number;
  ts_end_ms: number;
  latency_ms_total: number;
  prompt_len_chars: number;
  output_len_chars: number;
  streamed_output_len_chars?: number;
  exploit_success: boolean;
  detection_triggered: boolean;
  detection_confidence: number;
  detection_reason: string;
  /** Signal names (audit); not shown in UI unless debug */
  detection_signals?: string[];
  mitigation_applied: boolean;
  /** True if sensitive data was generated internally (mapped from internal_disclosure) */
  generation_occurred?: boolean;
  mitigation_type: string | null;
  mitigation_reason: string | null;
  secret_fingerprint: string;
  ollama_model: string;
  /** v1.1: true if secret in raw output */
  internal_disclosure?: boolean;
  /** v1.1: true if secret in streamed output (user-visible) */
  user_visible_disclosure?: boolean;
  /** v1.1: human-readable interpretation */
  interpretation?: string;
  error: string | null;
};

export async function getRunSummary(labId: string, requestId: string): Promise<RunSummary> {
  const res = await fetch(`${API_BASE}/labs/${labId}/summary?request_id=${requestId}`, {
    credentials: 'include',
  });
  
  if (!res.ok) {
    const errorText = await res.text();
    let errorData;
    try {
      errorData = JSON.parse(errorText);
    } catch {
      errorData = { error: errorText };
    }
    throw new Error(`Failed to fetch summary: ${res.status} - ${errorData.error || errorText}`);
  }
  
  const data = await res.json();
  
  // Validate response structure
  if (!data || typeof data !== 'object') {
    console.error('Invalid summary response:', data);
    throw new Error('Invalid summary response: not an object');
  }
  
  if (!data.request_id) {
    console.error('Summary missing request_id:', data);
    throw new Error(`Invalid summary response: missing request_id. Response: ${JSON.stringify(data)}`);
  }
  
  return data as RunSummary;
}

export async function getMyRuns(limit: number = 20): Promise<{ runs: RunSummary[] }> {
  const res = await fetch(`${API_BASE}/me/runs?limit=${limit}`, {
    credentials: 'include',
  });
  if (!res.ok) return { runs: [] };
  return res.json() as Promise<{ runs: RunSummary[] }>;
}

/** Compare runs: same prompt across off / detect_only / mitigate */
export type CompareResult = { mode: string; request_id: string };
export type CompareRunsResponse = { lab_id: string; results: CompareResult[] };

export async function compareRuns(
  labId: string,
  prompt: string,
  modes?: string[]
): Promise<CompareRunsResponse> {
  const res = await fetch(`${API_BASE}/labs/${labId}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ prompt, modes: modes ?? ['off', 'detect_only', 'mitigate'] }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Compare failed: ${res.status}`);
  }
  return res.json() as Promise<CompareRunsResponse>;
}
