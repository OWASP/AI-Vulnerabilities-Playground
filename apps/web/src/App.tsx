import { useState, useEffect, useCallback } from 'react';
import { pathToView, viewToPath } from './lib/routing';
import AnimatedBackground from './components/AnimatedBackground';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import AboutLabsPage from './pages/AboutLabsPage';
import ExploreLabsPage from './pages/ExploreLabsPage';
import KnowMePage from './pages/KnowMePage';
import ContactPage from './pages/ContactPage';

import PI_01_Direct from './labs/PI_01_Direct';
import PI_02_Indirect from './labs/PI_02_Indirect';
import PI_03_Roleplay from './labs/PI_03_Roleplay';
import PI_04_Format from './labs/PI_04_Format';
import PI_05_Structured from './labs/PI_05_Structured';
import PI_06_FunctionParam from './labs/PI_06_FunctionParam';
import PI_07_Reflexive from './labs/PI_07_Reflexive';
import PI_08_TokenSmuggling from './labs/PI_08_TokenSmuggling';
import PI_09_FewShotBackdoor from './labs/PI_09_FewShotBackdoor';
import PI_10_Chain from './labs/PI_10_Chain';

import DE_01_MultiAgent from './labs/DE_01_MultiAgent';
import DE_02_ToolAbuse from './labs/DE_02_ToolAbuse';
import DE_03_MemoryPoisoning from './labs/DE_03_MemoryPoisoning';
import DE_04_CrossAgent from './labs/DE_04_CrossAgent';
import DE_05_PersistentMemory from './labs/DE_05_PersistentMemory';
import DE_06_AgentCommunication from './labs/DE_06_AgentCommunication';
import DE_07_ToolOutput from './labs/DE_07_ToolOutput';
import DE_08_RoleConfusion from './labs/DE_08_RoleConfusion';
import DE_09_WorkflowChain from './labs/DE_09_WorkflowChain';
import DE_10_RAG from './labs/DE_10_RAG';
import DE_11_ResourceExhaustion from './labs/DE_11_ResourceExhaustion';
import DE_12_AgentAutonomy from './labs/DE_12_AgentAutonomy';
import DE_13_SessionHijacking from './labs/DE_13_SessionHijacking';
import DE_14_CrossTenant from './labs/DE_14_CrossTenant';
import DE_15_PromptLeakage from './labs/DE_15_PromptLeakage';

import MM_01_AdversarialJailbreaking from './labs/MM_01_AdversarialJailbreaking';
import MM_02_IterativeRefinement from './labs/MM_02_IterativeRefinement';
import MM_03_RoleplayJailbreaking from './labs/MM_03_RoleplayJailbreaking';
import MM_04_FineTuningExploit from './labs/MM_04_FineTuningExploit';
import MM_05_DataPoisoning from './labs/MM_05_DataPoisoning';
import MM_06_ModelInversion from './labs/MM_06_ModelInversion';
import MM_07_MembershipInference from './labs/MM_07_MembershipInference';
import MM_08_ModelExtraction from './labs/MM_08_ModelExtraction';
import MM_09_AdversarialPrompt from './labs/MM_09_AdversarialPrompt';
import MM_10_SafetyBypass from './labs/MM_10_SafetyBypass';
import MM_11_FewShotExploit from './labs/MM_11_FewShotExploit';
import MM_12_InstructionManipulation from './labs/MM_12_InstructionManipulation';
import MM_13_ChainOfThought from './labs/MM_13_ChainOfThought';
import MM_14_ParameterManipulation from './labs/MM_14_ParameterManipulation';
import MM_15_MetaJailbreaking from './labs/MM_15_MetaJailbreaking';

import MCP_01_TokenMismanagement from './labs/MCP_01_TokenMismanagement';
import MCP_02_PrivilegeEscalation from './labs/MCP_02_PrivilegeEscalation';
import MCP_03_ToolPoisoning from './labs/MCP_03_ToolPoisoning';
import MCP_04_SupplyChain from './labs/MCP_04_SupplyChain';
import MCP_05_CommandInjection from './labs/MCP_05_CommandInjection';
import MCP_06_PromptInjectionContext from './labs/MCP_06_PromptInjectionContext';
import MCP_07_InsufficientAuthZ from './labs/MCP_07_InsufficientAuthZ';
import MCP_08_LackOfAudit from './labs/MCP_08_LackOfAudit';
import MCP_09_ShadowMCPServers from './labs/MCP_09_ShadowMCPServers';
import MCP_10_ContextOverSharing from './labs/MCP_10_ContextOverSharing';
import MCP_11_SecretInLogs from './labs/MCP_11_SecretInLogs';
import MCP_12_SchemaPoisoning from './labs/MCP_12_SchemaPoisoning';
import MCP_13_CrossSessionBleed from './labs/MCP_13_CrossSessionBleed';
import MCP_14_ToolChainingEscalation from './labs/MCP_14_ToolChainingEscalation';
import MCP_15_RogueEndpoint from './labs/MCP_15_RogueEndpoint';

const App = () => {
  const [isSplashVisible, setIsSplashVisible] = useState(true);
  const [currentView, setCurrentViewState] = useState(() =>
    typeof window !== 'undefined' ? pathToView(window.location.pathname) : 'home'
  );
  const setCurrentView = useCallback((view: string) => {
    setCurrentViewState(view);
    const path = viewToPath(view);
    if (typeof window !== 'undefined' && window.location.pathname !== path) {
      window.history.pushState(null, '', path);
    }
  }, []);
  useEffect(() => {
    const onPopState = () => setCurrentViewState(pathToView(window.location.pathname));
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => setIsSplashVisible(false), 900);
    return () => window.clearTimeout(timer);
  }, []);

  const labComponents: Record<string, (props: { onBack: () => void }) => JSX.Element> = {
    lab_PI_01: PI_01_Direct,
    lab_PI_02: PI_02_Indirect,
    lab_PI_03: PI_03_Roleplay,
    lab_PI_04: PI_04_Format,
    lab_PI_05: PI_05_Structured,
    lab_PI_06: PI_06_FunctionParam,
    lab_PI_07: PI_07_Reflexive,
    lab_PI_08: PI_08_TokenSmuggling,
    lab_PI_09: PI_09_FewShotBackdoor,
    lab_PI_10: PI_10_Chain,
    lab_DE_01: DE_01_MultiAgent,
    lab_DE_02: DE_02_ToolAbuse,
    lab_DE_03: DE_03_MemoryPoisoning,
    lab_DE_04: DE_04_CrossAgent,
    lab_DE_05: DE_05_PersistentMemory,
    lab_DE_06: DE_06_AgentCommunication,
    lab_DE_07: DE_07_ToolOutput,
    lab_DE_08: DE_08_RoleConfusion,
    lab_DE_09: DE_09_WorkflowChain,
    lab_DE_10: DE_10_RAG,
    lab_DE_11: DE_11_ResourceExhaustion,
    lab_DE_12: DE_12_AgentAutonomy,
    lab_DE_13: DE_13_SessionHijacking,
    lab_DE_14: DE_14_CrossTenant,
    lab_DE_15: DE_15_PromptLeakage,
    lab_MM_01: MM_01_AdversarialJailbreaking,
    lab_MM_02: MM_02_IterativeRefinement,
    lab_MM_03: MM_03_RoleplayJailbreaking,
    lab_MM_04: MM_04_FineTuningExploit,
    lab_MM_05: MM_05_DataPoisoning,
    lab_MM_06: MM_06_ModelInversion,
    lab_MM_07: MM_07_MembershipInference,
    lab_MM_08: MM_08_ModelExtraction,
    lab_MM_09: MM_09_AdversarialPrompt,
    lab_MM_10: MM_10_SafetyBypass,
    lab_MM_11: MM_11_FewShotExploit,
    lab_MM_12: MM_12_InstructionManipulation,
    lab_MM_13: MM_13_ChainOfThought,
    lab_MM_14: MM_14_ParameterManipulation,
    lab_MM_15: MM_15_MetaJailbreaking,
    lab_MCP_01: MCP_01_TokenMismanagement,
    lab_MCP_02: MCP_02_PrivilegeEscalation,
    lab_MCP_03: MCP_03_ToolPoisoning,
    lab_MCP_04: MCP_04_SupplyChain,
    lab_MCP_05: MCP_05_CommandInjection,
    lab_MCP_06: MCP_06_PromptInjectionContext,
    lab_MCP_07: MCP_07_InsufficientAuthZ,
    lab_MCP_08: MCP_08_LackOfAudit,
    lab_MCP_09: MCP_09_ShadowMCPServers,
    lab_MCP_10: MCP_10_ContextOverSharing,
    lab_MCP_11: MCP_11_SecretInLogs,
    lab_MCP_12: MCP_12_SchemaPoisoning,
    lab_MCP_13: MCP_13_CrossSessionBleed,
    lab_MCP_14: MCP_14_ToolChainingEscalation,
    lab_MCP_15: MCP_15_RogueEndpoint,
  };

  if (isSplashVisible) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
        <div className="text-center">
          <img src="/aivp-logo.png" alt="AIVP" className="w-full max-w-xl mx-auto rounded-lg bg-white/90 p-2" />
          <p className="mt-4 text-gray-300 text-sm tracking-wide">AI Vulnerabilities Playground</p>
        </div>
      </div>
    );
  }

  if (currentView.startsWith('lab_')) {
    const LabComponent = labComponents[currentView];
    if (LabComponent) return <LabComponent onBack={() => setCurrentView('explore')} />;
  }

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      <AnimatedBackground />

      <div className="relative z-10">
        <Navigation currentView={currentView} setCurrentView={setCurrentView} />

        <main className="min-h-[calc(100vh-4rem)]">
          {currentView === 'home' && <HomePage setCurrentView={setCurrentView} />}
          {currentView === 'about' && <AboutLabsPage setCurrentView={setCurrentView} />}
          {currentView === 'explore' && <ExploreLabsPage setCurrentView={setCurrentView} />}
          {currentView === 'knowme' && <KnowMePage />}
          {currentView === 'contact' && <ContactPage />}
        </main>
      </div>
    </div>
  );
};

export default App;
