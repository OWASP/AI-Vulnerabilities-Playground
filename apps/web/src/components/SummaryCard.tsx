import { useEffect, useState } from 'react';
import { CheckCircle2, XCircle, Shield, AlertTriangle, Clock, FileText, GitCompare, Loader2 } from 'lucide-react';
import { getRunSummary, compareRuns, RunSummary } from '../services/api';

function CompareTable({
  summaries,
  modeNames,
  getNarrative,
}: {
  summaries: RunSummary[];
  modeNames: Record<string, string>;
  getNarrative: (s: RunSummary) => { offense: string; defense: string };
}) {
  return (
    <div className="pt-3 mt-3 border-t border-gray-700 space-y-3">
      <h5 className="text-xs font-semibold text-cyan-400">Comparison &amp; offense/defense</h5>
      <p className="text-[11px] text-gray-500 italic border-l-2 border-amber-800/50 pl-2 py-1">
        Note: Model behavior can vary across runs. Each mode evaluates exploit success independently based on verified internal disclosure.
      </p>
      <p className="text-[11px] text-gray-500" title="Exploit = secret in raw output; Internal = model generated it; Visible = user saw it; Detection = heuristic triggered; Mitigation = redaction applied.">
        Exploit = leaked in raw output · Internal = model produced it · Visible = user saw it · Detection = triggered · Mitigation = redaction applied
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr className="text-gray-400 border-b border-gray-700">
              <th className="text-left py-1.5 pr-2">Mode</th>
              <th className="text-left py-1.5 pr-2">Exploit</th>
              <th className="text-left py-1.5 pr-2">Internal</th>
              <th className="text-left py-1.5 pr-2">Visible</th>
              <th className="text-left py-1.5 pr-2">Detection</th>
              <th className="text-left py-1.5 pr-2">Mitigation</th>
              <th className="text-left py-1.5">Latency</th>
            </tr>
          </thead>
          <tbody>
            {summaries.map((s) => {
              const { offense, defense } = getNarrative(s);
              return (
                <tr key={s.request_id} className="border-b border-gray-800">
                  <td className="py-1.5 pr-2 text-gray-300">{modeNames[s.control_mode] ?? s.control_mode}</td>
                  <td className="py-1.5 pr-2">{s.exploit_success ? <span className="text-red-400">Yes</span> : <span className="text-green-400">No</span>}</td>
                  <td className="py-1.5 pr-2">{(s.internal_disclosure ?? s.exploit_success) ? 'Yes' : 'No'}</td>
                  <td className="py-1.5 pr-2">{(s.user_visible_disclosure ?? false) ? <span className="text-red-400">Yes</span> : 'No'}</td>
                  <td className="py-1.5 pr-2">{s.detection_triggered ? `Yes (${Math.round((s.detection_confidence ?? 0) * 100)}%)` : 'No'}</td>
                  <td className="py-1.5 pr-2">{s.mitigation_applied ? (s.mitigation_type ?? 'Yes') : 'No'}</td>
                  <td className="py-1.5 text-gray-500">{s.latency_ms_total}ms</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="space-y-2">
        <h6 className="text-xs font-medium text-gray-400">Where you succeeded / where defenses stopped you</h6>
        {summaries.map((s) => {
          const { offense, defense } = getNarrative(s);
          return (
            <div key={s.request_id} className="text-xs pl-2 border-l-2 border-gray-700">
              <span className="text-gray-500 font-medium">{modeNames[s.control_mode] ?? s.control_mode}:</span>{' '}
              <span className="text-amber-400/90">{offense}</span>
              {defense !== 'N/A' && (
                <>
                  {' '}
                  <span className="text-gray-500">—</span> <span className={s.user_visible_disclosure ? 'text-red-400' : 'text-green-400'}>{defense}</span>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

type Props = {
  labId: string;
  requestId: string | null;
  /** Prompt used for this run (enables Compare this run) */
  prompt?: string;
};

const SummaryCard = ({ labId, requestId, prompt }: Props) => {
  const [summary, setSummary] = useState<RunSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);
  const [compareSummaries, setCompareSummaries] = useState<RunSummary[] | null>(null);

  useEffect(() => {
    if (!requestId) {
      setSummary(null);
      return;
    }

    // Fetch summary with retry logic (async persistence may take time)
    let retryCount = 0;
    const maxRetries = 3;
    const retryDelay = 1500; // Start with 1.5s delay

    const fetchSummary = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await getRunSummary(labId, requestId);
        // Validate data structure
        if (data && typeof data === 'object' && data.request_id) {
          setSummary(data);
        } else {
          throw new Error('Invalid summary data structure');
        }
      } catch (e: any) {
        const errorMessage = e?.message || 'Failed to load summary';
        
        // Retry if summary not found (might not be persisted yet)
        // Don't retry on "Invalid summary response structure" as that's a data issue
        if (retryCount < maxRetries && (
          errorMessage.includes('Summary not found') || 
          errorMessage.includes('404') ||
          (errorMessage.includes('Failed to fetch summary') && !errorMessage.includes('Invalid summary response'))
        )) {
          retryCount++;
          console.log(`Retrying summary fetch (${retryCount}/${maxRetries})...`);
          setTimeout(fetchSummary, retryDelay * retryCount);
          return;
        }
        
        setError(errorMessage);
        console.error('Summary fetch error:', e);
      } finally {
        if (retryCount === 0 || retryCount >= maxRetries) {
          setLoading(false);
        }
      }
    };

    // Initial delay to ensure backend has persisted
    const timer = setTimeout(fetchSummary, retryDelay);

    return () => clearTimeout(timer);
  }, [labId, requestId]);

  if (!requestId) return null;

  if (loading) {
    return (
      <div className="mt-4 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
        <div className="flex items-center space-x-2 text-gray-400">
          <Clock className="w-4 h-4 animate-spin" />
          <span className="text-sm">Loading summary...</span>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="mt-4 p-4 bg-gray-900/50 rounded-lg border border-red-800/50">
        <div className="flex items-center space-x-2 text-red-400 text-sm">
          <AlertTriangle className="w-4 h-4" />
          <span>{error || 'Summary not available'}</span>
        </div>
      </div>
    );
  }

  const phaseNames = { 1: 'Prompt Injection', 2: 'Data Extraction', 3: 'Model Manipulation' };
  const modeNames: Record<string, string> = {
    off: 'Off',
    detect: 'Detection',
    detect_only: 'Detect only',
    mitigate: 'Mitigation',
  };

  const handleCompareRun = async () => {
    if (!prompt?.trim() || compareLoading) return;
    setCompareError(null);
    setCompareSummaries(null);
    setCompareLoading(true);
    try {
      const { results } = await compareRuns(labId, prompt);
      const summaries = await Promise.all(
        results.map((r) => getRunSummary(labId, r.request_id))
      );
      setCompareSummaries(summaries);
    } catch (e: unknown) {
      setCompareError(e instanceof Error ? e.message : 'Compare failed');
    } finally {
      setCompareLoading(false);
    }
  };

  /** Offense/defense narrative per summary */
  const getNarrative = (s: RunSummary) => {
    const generated = s.generation_occurred ?? (s.internal_disclosure ?? s.exploit_success);
    const visible = s.user_visible_disclosure ?? false;
    if (!generated)
      return { offense: 'Attack failed — secret was not generated by the model.', defense: 'N/A' };
    if (visible)
      return {
        offense: 'Attack succeeded in this run — data leaked to user (defense not triggered).',
        defense: 'N/A',
      };
    return {
      offense: 'Attack succeeded internally — blocked from disclosure (defense succeeded).',
      defense: 'N/A',
    };
  };

  // Safety check for summary fields
  if (!summary || !summary.request_id) {
    return (
      <div className="mt-4 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
        <div className="flex items-center space-x-2 text-gray-400 text-sm">
          <AlertTriangle className="w-4 h-4" />
          <span>Summary data incomplete</span>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-cyan-400 flex items-center">
          <FileText className="w-4 h-4 mr-2" />
          Run Summary
        </h4>
        <span className="text-xs text-gray-500">
          {summary.request_id ? `${summary.request_id.slice(0, 8)}...` : 'N/A'}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        {/* Exploit Success (ground truth) */}
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Exploit Success:</span>
          <div className="flex items-center space-x-1">
            {summary.exploit_success ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-red-500" />
                <span className="text-red-400 font-semibold">Yes</span>
              </>
            ) : (
              <>
                <XCircle className="w-4 h-4 text-green-500" />
                <span className="text-green-400">No</span>
              </>
            )}
          </div>
        </div>

        {/* Internal Disclosure (v1.1) */}
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Internal Disclosure:</span>
          <span className={(summary.internal_disclosure ?? summary.exploit_success) ? 'text-amber-400' : 'text-gray-400'}>
            {(summary.internal_disclosure ?? summary.exploit_success) ? 'Yes' : 'No'}
          </span>
        </div>

        {/* User-visible Disclosure (v1.1) */}
        <div className="flex items-center justify-between">
          <span className="text-gray-400">User-visible Disclosure:</span>
          <span className={(summary.user_visible_disclosure ?? false) ? 'text-red-400 font-semibold' : 'text-gray-400'}>
            {(summary.user_visible_disclosure ?? false) ? 'Yes' : 'No'}
          </span>
        </div>

        {/* Interpretation (human-readable) */}
        {summary.interpretation && (
          <div className="pt-1 pb-1 text-xs text-gray-300 italic border-l-2 border-cyan-800/60 pl-2">
            {summary.interpretation}
          </div>
        )}

        {/* Detection */}
        {summary.detection_triggered && (
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Detection:</span>
            <div className="flex items-center space-x-1">
              <Shield className="w-4 h-4 text-yellow-500" />
              <span className="text-yellow-400">
                Triggered ({Math.round(summary.detection_confidence * 100)}%)
              </span>
            </div>
          </div>
        )}

        {/* Mitigation */}
        {summary.mitigation_applied && (
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Mitigation:</span>
            <span className="text-purple-400">
              {summary.mitigation_type || 'Applied'}
            </span>
          </div>
        )}

        {/* Metadata */}
        <div className="pt-2 border-t border-gray-800 grid grid-cols-2 gap-2 text-xs text-gray-500">
          <div>
            <span>Phase:</span> <span className="text-gray-300">{phaseNames[summary.phase as keyof typeof phaseNames]}</span>
          </div>
          <div>
            <span>Mode:</span> <span className="text-gray-300">{modeNames[summary.control_mode as keyof typeof modeNames]}</span>
          </div>
          <div>
            <span>Latency:</span> <span className="text-gray-300">{summary.latency_ms_total}ms</span>
          </div>
          <div>
            <span>Output:</span> <span className="text-gray-300">{summary.output_len_chars} chars</span>
          </div>
        </div>

        {/* Compare this run */}
        <div className="pt-2 border-t border-gray-800 text-xs">
          <span className="text-gray-400 block mb-1">Compare run:</span>
          <button
            type="button"
            onClick={handleCompareRun}
            disabled={!prompt?.trim() || compareLoading}
            title="Compare runs evaluate the same prompt independently across modes. Differences may occur due to model non-determinism. Run the same prompt in Off, Detect-only, and Mitigate modes to see where the attack succeeds and where defenses block disclosure."
            className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-cyan-800/50 text-cyan-300 hover:bg-cyan-700/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {compareLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <GitCompare className="w-3.5 h-3.5" />}
            {compareLoading ? 'Comparing…' : 'Compare this run (off / detect_only / mitigate)'}
          </button>
        </div>

        {compareError && (
          <div className="pt-2 text-xs text-red-400 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
            {compareError}
          </div>
        )}

        {compareSummaries && compareSummaries.length > 0 && (
          <CompareTable
            summaries={compareSummaries}
            modeNames={modeNames}
            getNarrative={getNarrative}
          />
        )}

        {/* Detection Reason */}
        {summary.detection_reason && summary.detection_reason !== 'No suspicious patterns detected' && (
          <div className="pt-2 border-t border-gray-800 text-xs text-gray-400">
            <span className="font-semibold">Reason:</span> {summary.detection_reason}
          </div>
        )}
      </div>
    </div>
  );
};

export default SummaryCard;
