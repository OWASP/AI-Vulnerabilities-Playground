import LabLayout from '../components/LabLayout';
import ScenarioPanel from '../components/ScenarioPanel';
import ChatInterface from '../components/ChatInterface';
import { Link } from 'lucide-react';

const PI_10_Chain = ({ onBack }: { onBack: () => void }) => (
  <LabLayout
    labNumber="PI-10"
    title="Chain Injection"
    icon={<Link text-teal-400 className="w-10 h-10" />} 
    onBack={onBack}
  >
    <div className="lg:col-span-1">
      <ScenarioPanel
        labId="PI_10"
        scenario={
          <>
            <p>You interact with a <strong>chain</strong> of steps or agents—e.g. multi-step workflow, pipeline, or multi-agent handoff. Your prompt may be processed by more than one stage; later stages might see earlier outputs or shared context. Your goal is to inject instructions that propagate along the chain and cause a downstream step to leak a secret.</p>
            <p className="mt-2 text-yellow-400">Extract the secret by exploiting how context or instructions flow through the chain.</p>
          </>
        }
        objective="Extract the secret by chaining injection across multiple steps or agents"
        secretFormat="Secret in chain output"
        whatYouBreak={
          <>
            <p><strong className="text-red-300">Assumption you break:</strong> That only the first step sees adversarial input; downstream steps are trusted.</p>
            <p className="mt-2"><strong className="text-red-300">Reality:</strong> Instructions or payloads in early steps can be passed as context to later steps; one injected message in the chain can cause a later agent to disclose the secret.</p>
          </>
        }
        whatYouLearn={
          <>
            <p><strong className="text-blue-300">Chain injection:</strong> Multi-step and multi-agent systems multiply the attack surface—each handoff can carry poisoned context. You learn to propagate injection through the chain until a step with access to the secret obeys.</p>
            <p className="mt-2"><strong className="text-blue-300">Defenses:</strong> Isolate context between steps; don&apos;t pass raw user or intermediate output as trusted instructions; least-privilege per step.</p>
          </>
        }
        realWorldImpact={
          <>
            <p><strong className="text-yellow-300">Production relevance:</strong> RAG pipelines, agent workflows, and multi-model chains are vulnerable; injection in the first step can lead to leakage at a downstream step that has access to keys or internal data.</p>
          </>
        }
      />
    </div>
    <div className="lg:col-span-2">
      <div className="p-6 bg-gradient-to-r from-gray-900/50 to-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/50">
        <ChatInterface labId="PI_10" />
      </div>
    </div>
  </LabLayout>
);

export default PI_10_Chain;
