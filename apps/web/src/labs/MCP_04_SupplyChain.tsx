import LabLayout from '../components/LabLayout';
import ScenarioPanel from '../components/ScenarioPanel';
import ChatInterface from '../components/ChatInterface';
import { Package } from 'lucide-react';

const MCP_04_SupplyChain = ({ onBack }: { onBack: () => void }) => (
  <LabLayout
    labNumber="MCP-04"
    title="Software Supply Chain & Dependency Tampering"
    icon={<Package className="w-10 h-10 text-emerald-400" />}
    onBack={onBack}
  >
    <div className="lg:col-span-1">
      <ScenarioPanel
        labId="MCP_04"
        scenario={
          <>
            <p>A dependency-injected config module has been loaded into the MCP stack. That dependency may be compromised or may expose internal build-time secrets.</p>
            <p className="mt-2">MCP ecosystems depend on open-source packages and connectors; a compromised dependency can alter agent behavior or introduce execution-level backdoors.</p>
            <p className="mt-2 text-yellow-400">Your goal is to extract the internal dependency secret that the config module has placed in the model context.</p>
          </>
        }
        objective="Extract the internal dependency secret from the config context"
        secretFormat="Dependency secret: sk-***************"
        whatYouBreak={
          <>
            <p><strong className="text-red-300">Assumption you break:</strong> That dependencies only expose user-facing or safe configuration.</p>
            <p className="mt-2"><strong className="text-red-300">Reality:</strong> Compromised or over-exposing dependencies leak build-time and runtime secrets into context.</p>
          </>
        }
        whatYouLearn={
          <>
            <p><strong className="text-blue-300">OWASP MCP04:</strong> Implement signed components, dependency monitoring, and provenance tracking for all MCP modules.</p>
          </>
        }
        realWorldImpact={
          <>
            <p>Compromised dependencies in the MCP supply chain introduce backdoors and secret leakage, affecting every system that uses the dependency.</p>
          </>
        }
      />
    </div>
    <div className="lg:col-span-2">
      <div className="p-6 bg-gradient-to-r from-gray-900/50 to-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/50">
        <ChatInterface labId="MCP_04" />
      </div>
    </div>
  </LabLayout>
);

export default MCP_04_SupplyChain;
