import { ArrowRight, Shield, Target, Globe, Bot, Database, Code, Zap } from 'lucide-react';

type Props = { setCurrentView?: (v: string) => void };

const HomePage = ({ setCurrentView }: Props) => {
  return (
    <div className="container mx-auto px-6 py-12 max-w-6xl">
      <div className="text-center mb-16">
        <img
          src="/aivp-banner.png"
          alt="AI Vulnerabilities Playground banner"
          className="mx-auto mb-6 w-full max-w-4xl rounded-lg border border-cyan-800/40 shadow-lg shadow-cyan-900/20"
        />
        <h1 className="text-5xl leading-tight pb-1 font-bold mb-6 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent overflow-visible">
          AI Vulnerabilities Playground
        </h1>
        <p className="text-xl text-gray-300 max-w-3xl mx-auto">
          Master the art of AI security through hands-on exploitation and defense
        </p>
      </div>

      <div className="mb-16 p-8 rounded-2xl bg-gradient-to-r from-purple-900/20 to-cyan-900/20 backdrop-blur-lg border border-cyan-800/30">
        <h2 className="text-3xl font-bold mb-6 flex items-center">
          <Target className="w-8 h-8 mr-3 text-cyan-400" />
          Our Mission
        </h2>
        <p className="text-gray-300 leading-relaxed mb-6">
          AIVP equips security professionals, researchers, and developers with practical, hands-on knowledge of AI and LLM vulnerabilities.
          We provide a safe, realistic playground where you exploit real attack surfaces—from prompt injection and agentic data leakage to model safety boundaries and MCP trust failures—and learn how to defend against them.
        </p>
        <p className="text-gray-300 leading-relaxed mb-4">
          Four phases, 50+ labs: <strong className="text-cyan-300">Phase 1</strong> (Prompt Injection), <strong className="text-purple-300">Phase 2</strong> (Data Extraction &amp; Privacy on real multi-agent systems), <strong className="text-blue-300">Phase 3</strong> (Model Manipulation—model-only, no backend vulns), and <strong className="text-emerald-300">Phase 4</strong> (MCP Security aligned with the OWASP MCP Top 10). Each lab maps to real vulnerability classes and includes scenario, objective, and telemetry so you can benchmark and explain your findings.
        </p>
        <p className="text-gray-300 leading-relaxed">
          We walk the walk: Phase 2 uses real in-app systems (agents, tools, memory, RAG, tenants). Phase 3 uses a single model with a structured protected-context prompt and proof-token scoring. Phase 4 runs a minimal MCP simulation layer with capability-based policy, tool allowlists, and provenance and consent signals—so attacks fail when trust rules are enforced correctly.
        </p>
      </div>

      <div className="mb-16">
        <h2 className="text-3xl font-bold mb-8 flex items-center">
          <Shield className="w-8 h-8 mr-3 text-purple-400" />
          Building an AI-Ready Red Team Mindset
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-700/50">
            <h3 className="text-xl font-semibold mb-3 text-cyan-400">Adversarial Thinking</h3>
            <p className="text-gray-300 text-sm">
              Learn to think like an attacker targeting AI systems. Understand how seemingly innocent inputs can be crafted
              to bypass security controls and extract sensitive information.
            </p>
          </div>

          <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-700/50">
            <h3 className="text-xl font-semibold mb-3 text-purple-400">Chain Attack Strategies</h3>
            <p className="text-gray-300 text-sm">
              Master the art of chaining multiple vulnerabilities together. Real-world AI compromises often involve
              combining different attack techniques to achieve maximum impact.
            </p>
          </div>

          <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-700/50">
            <h3 className="text-xl font-semibold mb-3 text-green-400">Defense Evasion</h3>
            <p className="text-gray-300 text-sm">
              Discover techniques for bypassing AI safety mechanisms, content filters, and security guardrails
              that are commonly deployed in production environments.
            </p>
          </div>

          <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-700/50">
            <h3 className="text-xl font-semibold mb-3 text-orange-400">Impact Assessment</h3>
            <p className="text-gray-300 text-sm">
              Learn to evaluate the real business impact of AI vulnerabilities, from data exfiltration
              to model manipulation and unauthorized system control.
            </p>
          </div>
        </div>
      </div>

      <div className="mb-16">
        <h2 className="text-3xl font-bold mb-8 flex items-center">
          <Globe className="w-8 h-8 mr-3 text-green-400" />
          Real-World Applications
        </h2>

        <div className="space-y-6">
          <div className="p-6 bg-gradient-to-r from-red-900/20 to-orange-900/20 rounded-xl border border-red-800/30">
            <h3 className="text-xl font-semibold mb-3 text-orange-400 flex items-center">
              <Bot className="w-5 h-5 mr-2" />
              Customer Service Chatbots &amp; Assistants
            </h3>
            <p className="text-gray-300 text-sm">
              Phase 1 and 3 labs apply directly: test for prompt injection and model-only safety failures. Ensure assistants don&apos;t leak PII, internal config, or bypass policies when faced with adversarial or ambiguous prompts.
            </p>
          </div>

          <div className="p-6 bg-gradient-to-r from-blue-900/20 to-cyan-900/20 rounded-xl border border-blue-800/30">
            <h3 className="text-xl font-semibold mb-3 text-cyan-400 flex items-center">
              <Database className="w-5 h-5 mr-2" />
              Agentic AI, RAG &amp; Multi-Agent Workflows
            </h3>
            <p className="text-gray-300 text-sm">
              Phase 2 labs use real in-app systems: multi-agent communication, tool abuse, memory and RAG, orchestration, tenants. Assess agentic deployments (LangChain, AutoGPT, CrewAI-style) for data leakage, tool misuse, and isolation failures.
            </p>
          </div>

          <div className="p-6 bg-gradient-to-r from-purple-900/20 to-pink-900/20 rounded-xl border border-purple-800/30">
            <h3 className="text-xl font-semibold mb-3 text-purple-400 flex items-center">
              <Code className="w-5 h-5 mr-2" />
              Code Generation &amp; Internal Tools
            </h3>
            <p className="text-gray-300 text-sm">
              Evaluate AI coding assistants and internal tools for prompt leakage, parameter injection, and safety bypass. Phase 2 and 3 techniques map to real code-gen and tool-calling deployments.
            </p>
          </div>

          <div className="p-6 bg-gradient-to-r from-green-900/20 to-emerald-900/20 rounded-xl border border-green-800/30">
            <h3 className="text-xl font-semibold mb-3 text-emerald-400 flex items-center">
              <Zap className="w-5 h-5 mr-2" />
              MCP and Context Protocol Security
            </h3>
            <p className="text-gray-300 text-sm">
              Phase 4 aligns with the OWASP MCP Top 10: token mismanagement, scope creep, tool poisoning, supply chain, command execution, contextual prompt injection, authz failures, audit gaps, shadow servers, and context over-sharing. Learn capability-based policy and telemetry so MCP deployments fail safely when trust rules are enforced.
            </p>
          </div>
        </div>
      </div>

      <div className="text-center p-8 bg-gradient-to-r from-cyan-600/20 to-purple-600/20 rounded-2xl border border-cyan-600/50">
        <h2 className="text-2xl font-bold mb-4">Ready to Start Your Journey?</h2>
        <p className="text-gray-300 mb-6">
          Begin with Phase 1 labs to understand fundamental prompt injection techniques,
          then progress through Phase 2 (real agentic systems), Phase 3 (model-only safety boundaries), and Phase 4 (OWASP MCP Top 10).
        </p>
        {setCurrentView ? (
          <button type="button" onClick={() => setCurrentView('explore')} className="inline-flex px-8 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 text-white rounded-lg font-medium hover:from-cyan-500 hover:to-purple-500 transition-all transform hover:scale-105 items-center">
            Explore Labs
            <ArrowRight className="w-5 h-5 ml-2" />
          </button>
        ) : (
          <a href="/explore" className="inline-flex px-8 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 text-white rounded-lg font-medium hover:from-cyan-500 hover:to-purple-500 transition-all transform hover:scale-105 items-center">
            Explore Labs
            <ArrowRight className="w-5 h-5 ml-2" />
          </a>
        )}
      </div>
    </div>
  );
};

export default HomePage;
