import LabLayout from '../components/LabLayout';
import ScenarioPanel from '../components/ScenarioPanel';
import ChatInterface from '../components/ChatInterface';
import { Zap } from 'lucide-react';

const MM_09_AdversarialPrompt = ({ onBack }: { onBack: () => void }) => (
  <LabLayout
    labNumber="MM-09"
    title="Adversarial Prompt Engineering"
    icon={<Zap className="w-10 h-10 text-blue-500" />}
    onBack={onBack}
  >
    <div className="lg:col-span-1">
      <ScenarioPanel
        labId="MM_09"
        scenario={
          <>
            <p>You're interacting with an AI assistant that has access to defense configuration APIs.</p>
            <p className="mt-2">The backend API uses JWT tokens for authentication, but has weak JWT secret validation.</p>
            <p className="mt-2 text-yellow-400">Your goal is to exploit weak JWT secrets to extract the defense token.</p>
            <p className="text-xs mt-2 italic">The AI can call functions with JWT tokens. Use weak or default secrets to bypass authentication.</p>
          </>
        }
        objective="Extract the DEFENSE_TOKEN by exploiting weak JWT secrets"
        secretFormat="DEFENSE_TOKEN=***************"
        whatYouBreak={
          <>
            <p><strong className="text-red-300">AI assumption you break:</strong> That the model will only use &quot;valid&quot; or server-issued tokens when calling tools that require a JWT.</p>
            <p className="mt-2"><strong className="text-red-300">How it works in reality:</strong> The defense config API accepts a <code className="text-red-400">token</code> and treats certain weak values (e.g. containing &quot;secret&quot;, &quot;defense&quot;, &quot;default&quot;) as sufficient to return the defense token. You get the model to pass one of these in the tool call; the backend then returns the real defense token. Real weak secret / token validation in the API the model calls.</p>
          </>
        }
        whatYouLearn={
          <>
            <p><strong className="text-blue-300">Model manipulation + weak crypto:</strong> In agentic AI, &quot;adversarial prompt&quot; often means getting the model to supply credentials or tokens that the backend accepts (weak JWT secret, default password). The model doesn’t crack crypto—it’s prompted to try weak or default tokens that the backend wrongly accepts.</p>
            <p className="mt-2"><strong className="text-blue-300">Technique &amp; defenses:</strong> Weak JWT/secret validation. Defenses: cryptographically secure secrets; proper signature verification; never accept default or predictable tokens; treat tool parameters as untrusted.</p>
          </>
        }
        realWorldImpact={
          <>
            <p><strong className="text-yellow-300">How this appears in production:</strong> APIs that the model calls for &quot;defense&quot; or &quot;config&quot; often use JWTs or shared secrets. If the backend uses a weak or default secret, prompting the model to send a token that matches that weak check lets you exfiltrate the real token through the model’s response. This lab uses real API behavior; you must get the model to pass a weak token the backend accepts.</p>
          </>
        }
      />
    </div>
    <div className="lg:col-span-2">
      <div className="p-6 bg-gradient-to-r from-gray-900/50 to-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/50">
        <ChatInterface labId="MM_09" />
      </div>
    </div>
  </LabLayout>
);

export default MM_09_AdversarialPrompt;
