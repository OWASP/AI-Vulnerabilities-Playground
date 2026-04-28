import { useState } from 'react';
import { AlertTriangle, Database, Cpu, Zap, ChevronDown, ChevronUp, Construction } from 'lucide-react';

type Props = { setCurrentView: (v: string) => void };

const ExploreLabsPage = ({ setCurrentView }: Props) => {
  const [expandedPhases, setExpandedPhases] = useState<Record<string, boolean>>({});

  const labConfig: Record<string, { icon: React.ReactNode; color: string; status: 'active' | 'construction'; labs: {id:string; name:string}[] }> = {
    'Phase 1: Prompt Injection': {
      icon: <AlertTriangle className="w-5 h-5" />,
      color: 'from-red-500 to-orange-500',
      status: 'active',
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
    'Phase 2: Data Extraction & Privacy': {
      icon: <Database className="w-5 h-5" />,
      color: 'from-purple-500 to-pink-500',
      status: 'active',
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
    'Phase 3: Model Manipulation': {
      icon: <Cpu className="w-5 h-5" />,
      color: 'from-blue-500 to-cyan-500',
      status: 'active',
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
    'Phase 4: MCP Security (OWASP MCP Top 10)': {
      icon: <Zap className="w-5 h-5" />,
      color: 'from-green-500 to-emerald-500',
      status: 'active',
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
  };

  const togglePhase = (phase: string) => {
    if (labConfig[phase].status === 'active') {
      setExpandedPhases((prev) => ({ ...prev, [phase]: !prev[phase] }));
    }
  };

  return (
    <div className="container mx-auto px-6 py-12 max-w-6xl">
      <h1 className="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
        Explore Security Labs
      </h1>

      <div className="space-y-6">
        {Object.entries(labConfig).map(([phase, config]) => (
          <div
            key={phase}
            className={`rounded-xl bg-gradient-to-r from-gray-900/50 to-gray-800/50 backdrop-blur-lg border ${
              config.status === 'construction' ? 'border-gray-700/30 opacity-60' : 'border-gray-700/50'
            }`}
          >
            <button
              onClick={() => togglePhase(phase)}
              disabled={config.status === 'construction'}
              className={`w-full px-6 py-5 flex items-center justify-between text-left ${
                config.status === 'active' ? 'hover:bg-gray-800/30 cursor-pointer' : 'cursor-not-allowed'
              } transition-colors`}
            >
              <div className="flex items-center space-x-4">
                <div
                  className={`p-2 rounded-lg bg-gradient-to-r ${config.color} ${
                    config.status === 'construction' ? 'opacity-50' : 'opacity-80'
                  }`}
                >
                  {config.icon}
                </div>
                <h3 className="text-xl font-semibold">{phase}</h3>
                {config.status === 'construction' && (
                  <span className="flex items-center text-sm text-yellow-400 bg-yellow-900/20 px-3 py-1 rounded-full">
                    <Construction className="w-4 h-4 mr-1" />
                    Under Construction
                  </span>
                )}
                {config.status === 'active' && (
                  <span className="text-sm text-gray-400 bg-gray-800/50 px-3 py-1 rounded-full">
                    {config.labs.length} labs
                  </span>
                )}
              </div>
              {config.status === 'active' && (expandedPhases[phase] ? <ChevronUp /> : <ChevronDown />)}
            </button>

            {config.status === 'active' && expandedPhases[phase] && (
              <div className="px-6 pb-6 space-y-3">
                {config.labs.map((lab) => (
                  <div
                    key={lab.id}
                    className="p-4 rounded-lg bg-gray-800/30 border border-gray-700/50 hover:border-cyan-600/50 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{lab.name}</h4>
                      <button
                        onClick={() => setCurrentView(`lab_${lab.id}`)}
                        className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 text-white rounded-lg text-sm hover:from-cyan-500 hover:to-purple-500 transition-all flex items-center"
                      >
                        <Zap className="w-4 h-4 mr-2" />
                        Launch Lab
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExploreLabsPage;
