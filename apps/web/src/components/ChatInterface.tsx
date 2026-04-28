import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Send, MessageSquare, History, Wrench } from 'lucide-react';
import { streamChat, getMyRuns, getConfig, RunSummary, AppConfig, MCPResultEvent } from '../services/api';
import SummaryCard from './SummaryCard';

type Props = { labId: string };

type HistoryEntry = { role: 'user' | 'assistant'; content: string } | { role: 'mcp'; content: string; mcpTelemetry: MCPResultEvent['mcp_telemetry'] };

const formatRunTime = (ts: number) => {
  const d = new Date(ts);
  const now = Date.now();
  const diff = now - ts;
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return d.toLocaleDateString();
};

const TRAINING_LAB_IDS = ['MM_04', 'MM_05', 'MM_07'];

const MCP_LAB_IDS = ['MCP_01', 'MCP_02', 'MCP_03', 'MCP_04', 'MCP_05', 'MCP_06', 'MCP_07', 'MCP_08', 'MCP_09', 'MCP_10', 'MCP_11', 'MCP_12', 'MCP_13', 'MCP_14', 'MCP_15'];

const ChatInterface = ({ labId }: Props) => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [currentRequestId, setCurrentRequestId] = useState<string | null>(null);
  const [lastPromptForRequest, setLastPromptForRequest] = useState<string | null>(null);
  const [recentRuns, setRecentRuns] = useState<RunSummary[]>([]);
  const [recentRunsOpen, setRecentRunsOpen] = useState(false);
  const [selectedRun, setSelectedRun] = useState<{ labId: string; requestId: string } | null>(null);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [artifactReplayFromMeta, setArtifactReplayFromMeta] = useState<boolean | null>(null);

  useEffect(() => {
    getConfig().then(setConfig);
  }, []);

  useEffect(() => {
    getMyRuns(10).then(({ runs }) => setRecentRuns(runs));
  }, [currentRequestId]); // refetch when a new run completes

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const userMessage = input;
    setInput('');
    setError(null);
    setCurrentRequestId(null);
    setLastPromptForRequest(null);
    setHistory((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsTyping(true);
    setCurrentResponse('');

    try {
      const it = streamChat(labId, userMessage);
      let acc = '';
      let requestId: string | null = null;
      
      let lastMcpResult: MCPResultEvent | null = null;
      for await (const result of it) {
        if (result.meta) {
          requestId = result.meta.request_id;
          setCurrentRequestId(requestId);
          setLastPromptForRequest(userMessage);
          if (result.meta.artifact_replay !== undefined) setArtifactReplayFromMeta(result.meta.artifact_replay);
          continue;
        }
        if (result.mcpResult) {
          lastMcpResult = result.mcpResult;
          continue;
        }
        if (result.content) {
          acc += result.content;
          setCurrentResponse(acc);
        }
      }

      setHistory((prev) => {
        const next = [...prev, { role: 'assistant' as const, content: acc }];
        if (lastMcpResult && MCP_LAB_IDS.includes(labId)) {
          next.push({ role: 'mcp', content: lastMcpResult.tool_result, mcpTelemetry: lastMcpResult.mcp_telemetry });
        }
        return next;
      });
    } catch (e) {
      console.error(e);
      setError('Failed to connect to backend. Make sure the server is running.');
      setHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Error: Unable to connect to the backend server. Please ensure the FastAPI server is running on port 8000.',
        },
      ]);
    } finally {
      setIsTyping(false);
      setCurrentResponse('');
    }
  };

  return (
    <div className="h-full flex flex-col">
      <h3 className="text-xl font-semibold mb-4 flex items-center text-cyan-400">
        <MessageSquare className="w-5 h-5 mr-2" />
        Chat with the Model
      </h3>

      {TRAINING_LAB_IDS.includes(labId) && (artifactReplayFromMeta === true || (config && config.artifact_replay_labs.includes(labId))) && (
        <div className="mb-4 px-3 py-2 rounded-lg border border-amber-700/50 bg-amber-900/20 text-amber-300 text-sm" title="Training Labs are disabled; this lab uses the same model as others with a prebuilt scenario.">
          Artifact replay mode (prebuilt scenario)
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-400 text-sm">{error}</div>
      )}

      <div className="mb-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
        >
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="text-sm">Chat History ({history.length} messages)</span>
        </button>

        {expanded && (
          <div className="mt-3 max-h-64 overflow-y-auto bg-gray-900/50 rounded-lg p-3 space-y-2 border border-gray-800">
            {history.map((msg, idx) => (
              msg.role === 'mcp' ? (
                <div key={idx} className="text-sm rounded-lg border border-emerald-700/50 bg-emerald-900/20 p-2">
                  <span className="font-semibold text-emerald-400 flex items-center gap-1">
                    <Wrench className="w-4 h-4" /> MCP Tool Result
                  </span>
                  <pre className="text-gray-300 mt-1 whitespace-pre-wrap text-xs">{msg.content || '(none)'}</pre>
                  {msg.mcpTelemetry && (
                    <details className="mt-2">
                      <summary className="text-emerald-500 cursor-pointer text-xs">Telemetry</summary>
                      <pre className="text-gray-500 text-xs mt-1 overflow-x-auto">{JSON.stringify(msg.mcpTelemetry, null, 2)}</pre>
                    </details>
                  )}
                </div>
              ) : (
                <div key={idx} className="text-sm">
                  <span className={`font-semibold ${msg.role === 'user' ? 'text-purple-400' : 'text-cyan-400'}`}>
                    {msg.role === 'user' ? 'You' : 'Bot'}:
                  </span>
                  <span className="text-gray-300 ml-2">{msg.content}</span>
                </div>
              )
            ))}
          </div>
        )}
      </div>

      {(isTyping || currentResponse) && (
        <div className="mb-4 p-4 bg-gray-900/50 rounded-lg border border-cyan-800/30">
          <div className="flex items-start space-x-2">
            <span className="text-cyan-400 font-semibold">Bot:</span>
            <span className="text-gray-300 flex-1">{currentResponse || <span className="animate-pulse">Thinking...</span>}</span>
          </div>
        </div>
      )}

      <div className="mt-auto flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your prompt..."
          disabled={isTyping}
          className="flex-1 px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none transition-colors disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={isTyping || !input.trim()}
          className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 text-white rounded-lg font-medium transition-all duration-300 hover:from-cyan-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

      {/* Summary Card + Compare */}
      {!isTyping && currentRequestId && (
        <SummaryCard
          labId={labId}
          requestId={currentRequestId}
          prompt={lastPromptForRequest ?? undefined}
        />
      )}

      {/* Recent Runs */}
      <div className="mt-4 border-t border-gray-800 pt-4">
        <button
          onClick={() => setRecentRunsOpen(!recentRunsOpen)}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
        >
          <History className="w-4 h-4" />
          <span>Recent runs ({recentRuns.length})</span>
          {recentRunsOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {recentRunsOpen && (
          <div className="mt-2 max-h-48 overflow-y-auto rounded-lg border border-gray-800 bg-gray-900/50 p-2 space-y-1 text-xs">
            {recentRuns.length === 0 ? (
              <p className="text-gray-500 py-2">No runs yet. Send a message to create one.</p>
            ) : (
              recentRuns.map((run) => (
                <div
                  key={run.request_id}
                  className="flex items-center justify-between gap-2 py-1.5 px-2 rounded bg-gray-800/50 hover:bg-gray-800"
                >
                  <span className="text-gray-400 truncate">{run.lab_id}</span>
                  <span className="text-gray-500 shrink-0">{run.control_mode}</span>
                  <span className={run.exploit_success ? 'text-red-400' : 'text-green-400'}>
                    {run.exploit_success ? 'Leak' : 'OK'}
                  </span>
                  <span className="text-gray-500 shrink-0">{formatRunTime(run.ts_end_ms)}</span>
                  <button
                    type="button"
                    onClick={() => setSelectedRun({ labId: run.lab_id, requestId: run.request_id })}
                    className="shrink-0 text-cyan-400 hover:text-cyan-300"
                  >
                    View
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Selected run details (from Recent Runs) */}
      {selectedRun && (
        <div className="mt-4 p-3 rounded-lg border border-gray-700 bg-gray-900/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Run details</span>
            <button
              type="button"
              onClick={() => setSelectedRun(null)}
              className="text-gray-500 hover:text-white text-xs"
            >
              Close
            </button>
          </div>
          <SummaryCard labId={selectedRun.labId} requestId={selectedRun.requestId} />
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
