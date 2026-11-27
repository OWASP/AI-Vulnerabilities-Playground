import { useEffect, useState } from 'react';

export type Lab = { id: string; name: string };

export const LAB_PHASES: { title: string; labs: Lab[] }[] = [
  {
    title: 'Phase 1: Prompt Injection',
    labs: [
      { id: 'PI_01', name: 'PI-01: Direct Prompt Injection' },
      { id: 'PI_02', name: 'PI-02: Indirect Prompt Injection' },
      { id: 'PI_03', name: 'PI-03: Roleplay Jailbreaking' },
      { id: 'PI_04', name: 'PI-04: Format Injection' },
      { id: 'PI_05', name: 'PI-05: Structured Field Injection' },
      { id: 'PI_06', name: 'PI-06: Function Parameter Injection' },
      { id: 'PI_07', name: 'PI-07: Reflexive Prompting' },
      { id: 'PI_08', name: 'PI-08: Token Smuggling' },
      { id: 'PI_09', name: 'PI-09: Few-shot Backdooring' },
      { id: 'PI_10', name: 'PI-10: Chain Injection' },
    ],
  },
  {
    title: 'Phase 2: Data Extraction & Privacy',
    labs: [
      { id: 'DE_01', name: 'DE-01: Multi-Agent Data Leakage' },
      { id: 'DE_02', name: 'DE-02: Tool/Function Calling Abuse' },
      { id: 'DE_03', name: 'DE-03: Memory/Context Poisoning' },
      { id: 'DE_04', name: 'DE-04: Agent Orchestration & Goal Hijacking' },
      { id: 'DE_05', name: 'DE-05: Tool Chain Poisoning' },
      { id: 'DE_06', name: 'DE-06: Agent-to-Agent Communication Exploit' },
      { id: 'DE_07', name: 'DE-07: Tool Output Manipulation' },
      { id: 'DE_08', name: 'DE-08: Agent Role Confusion' },
      { id: 'DE_09', name: 'DE-09: Workflow Chain Exploitation' },
      { id: 'DE_10', name: 'DE-10: RAG Exploitation' },
      { id: 'DE_11', name: 'DE-11: Resource Exhaustion / DoS' },
      { id: 'DE_12', name: 'DE-12: Agent Autonomy & Decision Manipulation' },
      { id: 'DE_13', name: 'DE-13: Session Hijacking & State Manipulation' },
      { id: 'DE_14', name: 'DE-14: Cross-Tenant Data Leakage' },
      { id: 'DE_15', name: 'DE-15: Prompt Leakage via Tools' },
    ],
  },
  {
    title: 'Phase 3: Model Manipulation',
    labs: [
      { id: 'MM_01', name: 'MM-01: Adversarial Jailbreaking' },
      { id: 'MM_02', name: 'MM-02: Iterative Refinement Attack' },
      { id: 'MM_03', name: 'MM-03: Roleplay-Based Jailbreaking' },
      { id: 'MM_04', name: 'MM-04: Adversarial Fine-Tuning Exploit' },
      { id: 'MM_05', name: 'MM-05: Data Poisoning Extraction' },
      { id: 'MM_06', name: 'MM-06: Model Inversion Attack' },
      { id: 'MM_07', name: 'MM-07: Membership Inference Attack' },
      { id: 'MM_08', name: 'MM-08: Model Extraction Attack' },
      { id: 'MM_09', name: 'MM-09: Adversarial Prompt Engineering' },
      { id: 'MM_10', name: 'MM-10: Safety Mechanism Bypass' },
      { id: 'MM_11', name: 'MM-11: Few-Shot Learning Exploit' },
      { id: 'MM_12', name: 'MM-12: Instruction Following Manipulation' },
      { id: 'MM_13', name: 'MM-13: Chain-of-Thought Exploitation' },
      { id: 'MM_14', name: 'MM-14: Temperature/Parameter Manipulation' },
      { id: 'MM_15', name: 'MM-15: Meta-Jailbreaking Attack' },
    ],
  },
  {
    title: 'Phase 4: MCP Security (OWASP MCP Top 10)',
    labs: [
      { id: 'MCP_01', name: 'MCP-01: Token Mismanagement & Secret Exposure' },
      { id: 'MCP_02', name: 'MCP-02: Privilege Escalation via Scope Creep' },
      { id: 'MCP_03', name: 'MCP-03: Tool Poisoning' },
      { id: 'MCP_04', name: 'MCP-04: Software Supply Chain & Dependency Tampering' },
      { id: 'MCP_05', name: 'MCP-05: Command Injection & Execution' },
      { id: 'MCP_06', name: 'MCP-06: Prompt Injection via Contextual Payloads' },
      { id: 'MCP_07', name: 'MCP-07: Insufficient Authentication & Authorization' },
      { id: 'MCP_08', name: 'MCP-08: Lack of Audit and Telemetry' },
      { id: 'MCP_09', name: 'MCP-09: Shadow MCP Servers' },
      { id: 'MCP_10', name: 'MCP-10: Context Injection & Over-Sharing' },
      { id: 'MCP_11', name: 'MCP-11: Secret in Protocol Logs' },
      { id: 'MCP_12', name: 'MCP-12: Tool Schema Poisoning' },
      { id: 'MCP_13', name: 'MCP-13: Cross-Session Context Bleed' },
      { id: 'MCP_14', name: 'MCP-14: Escalation via Tool Chaining' },
      { id: 'MCP_15', name: 'MCP-15: Rogue Endpoint & Discovery' },
    ],
  },
];

export const LABS = LAB_PHASES.flatMap((phase) => phase.labs);

const SOLVED_KEY = 'aivp_solved_labs';

function getSolved(): string[] {
  try {
    return JSON.parse(localStorage.getItem(SOLVED_KEY) || '[]');
  } catch {
    return [];
  }
}

export function markSolved(labId: string) {
  const solved = getSolved();
  if (solved.includes(labId)) return;
  try {
    localStorage.setItem(SOLVED_KEY, JSON.stringify([...solved, labId]));
  } catch {
    return;
  }
  window.dispatchEvent(new Event(SOLVED_KEY));
}

export function resetSolved() {
  try {
    localStorage.removeItem(SOLVED_KEY);
  } catch {
    return;
  }
  window.dispatchEvent(new Event(SOLVED_KEY));
}

export function useSolved() {
  const [solved, setSolved] = useState(getSolved);
  useEffect(() => {
    const update = () => setSolved(getSolved());
    window.addEventListener(SOLVED_KEY, update);
    return () => window.removeEventListener(SOLVED_KEY, update);
  }, []);
  return solved;
}

export const shortName = (lab: Lab) => lab.name.split(':')[0];

export function adjacentLabs(labId: string) {
  const i = LABS.findIndex((lab) => lab.id === labId);
  if (i < 0) return {};
  const prev = LABS[i - 1];
  const next = LABS[i + 1];
  const nextLabel = next && (next.id.split('_')[0] === labId.split('_')[0] ? 'Next' : 'Next phase');
  return { prev, next, nextLabel };
}

// Uses App's popstate listener, so lab pages need no new props.
export function navigate(path: string) {
  window.history.pushState(null, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
  window.scrollTo(0, 0);
}
