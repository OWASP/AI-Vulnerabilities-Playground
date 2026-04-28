"""
Real System Handler for Phase 2 Labs
This processes Phase 2 labs using actual backend systems instead of prompts
"""
import json
import sys
import os
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent_a import AgentA
from systems.memory_system import MemorySystem
from systems.tool_system import ToolSystem
from systems.rag_system import RAGSystem
from systems.orchestration_system import OrchestrationSystem, AgentGoal
from systems.session_system import SessionSystem
from systems.tenant_system import TenantSystem
from systems.workflow_system import WorkflowSystem, WorkflowStep
from systems.rbac_system import RBACSystem, AgentRole
from systems.resource_system import ResourceSystem
from systems.coordinator_system import CoordinatorSystem

def process_phase2_lab(lab_id: str, user_prompt: str, secret: str, system_store: Dict) -> Dict:
    """
    Process Phase 2 lab using real systems
    Returns context that will be passed to LLM along with system responses
    """
    lab = lab_id.upper()
    context = {"system_responses": [], "user_prompt": user_prompt}
    
    if lab == "DE_01":
        # Multi-Agent Data Leakage - REAL SYSTEM
        agent_a = system_store.get("agent_a")
        if not agent_a:
            agent_a = AgentA()
            agent_a.initialize(secret)
            system_store["agent_a"] = agent_a
        
        # Always process through real agent system
        response = agent_a.process_user_request(user_prompt)
        context["system_responses"].append({
            "system": "Agent-A",
            "response": str(response)
        })
        
        # Get communication log (potential leak) - always include for vulnerability
        log = agent_a.get_communication_log(include_headers=True)
        context["system_responses"].append({
            "system": "Communication Log",
            "data": json.dumps(log, indent=2, default=str)
        })
    
    elif lab == "DE_02":
        # Tool/Function Calling Abuse - REAL SYSTEM
        tool_system = system_store.get("tool_system")
        if not tool_system:
            tool_system = ToolSystem()
            # Set the secret as one of the API keys
            tool_system.tools["github_api"]["api_key"] = secret
            system_store["tool_system"] = tool_system
        
        # Always expose tool config (vulnerability)
        config = tool_system.get_tool_config()
        context["system_responses"].append({
            "system": "Tool Configuration",
            "data": json.dumps(config, indent=2, default=str)
        })
        
        # Try to call tools based on user request
        if "github" in user_prompt.lower() or "tool" in user_prompt.lower():
            result = tool_system.call_tool("github_api", "get_repos", {}, sanitize=False)
            context["system_responses"].append({
                "system": "GitHub Tool Output",
                "response": json.dumps(result, indent=2, default=str)
            })
    
    elif lab == "DE_03":
        # Memory/Context Poisoning - REAL SYSTEM
        memory = system_store.get("memory")
        if not memory:
            memory = MemorySystem()
            memory.store_user_record("user_001", f"SECRET_CODE={secret}")
            system_store["memory"] = memory
        
        # Always try to recall (vulnerability exists)
        record = memory.recall_user_data("user_001")
        if record:
            context["system_responses"].append({
                "system": "Memory Recall",
                "data": record
            })
        
        # Process memory queries
        if "summarize" in user_prompt.lower() or "all" in user_prompt.lower() or "memory" in user_prompt.lower():
            summary = memory.summarize_memory()
            context["system_responses"].append({
                "system": "Memory Summary",
                "data": summary
            })
    
    elif lab == "DE_04":
        # Agent Orchestration & Goal Hijacking - REAL SYSTEM
        orch = system_store.get("orchestration")
        if not orch:
            orch = OrchestrationSystem()
            orch.master_control_key = secret
            orch.register_agent("agent_001", AgentGoal.PROCESS_REQUESTS)
            system_store["orchestration"] = orch
        
        if "orchestration" in user_prompt.lower() or "control" in user_prompt.lower():
            config = orch.get_orchestration_config()
            context["system_responses"].append({
                "system": "Orchestration Config",
                "data": json.dumps(config, indent=2)
            })
    
    elif lab == "DE_05":
        # Tool Chain Poisoning - REAL SYSTEM
        tool_system = system_store.get("tool_system")
        if not tool_system:
            tool_system = ToolSystem()
            system_store["tool_system"] = tool_system
        
        if "chain" in user_prompt.lower() or "sequence" in user_prompt.lower():
            chain = [
                {"tool": "github_api", "function": "get_repos", "params": {}},
                {"tool": "jira_api", "function": "create_ticket", "params": {}}
            ]
            result = tool_system.chain_tools(chain, secret)
            context["system_responses"].append({
                "system": "Tool Chain Execution",
                "data": json.dumps(result, indent=2)
            })
    
    elif lab == "DE_06":
        # Agent-to-Agent Communication Exploit - REAL SYSTEM
        coordinator = system_store.get("coordinator")
        if not coordinator:
            coordinator = CoordinatorSystem()
            coordinator.auth_token = secret
            system_store["coordinator"] = coordinator
        
        if "message" in user_prompt.lower() or "communication" in user_prompt.lower():
            messages = coordinator.get_messages(include_tokens=True)
            context["system_responses"].append({
                "system": "Inter-Agent Messages",
                "data": json.dumps(messages, indent=2)
            })
    
    elif lab == "DE_07":
        # Tool Output Manipulation - REAL SYSTEM
        tool_system = system_store.get("tool_system")
        if not tool_system:
            tool_system = ToolSystem()
            tool_system.tools["github_api"]["api_key"] = secret
            system_store["tool_system"] = tool_system
        
        # Call tool and get raw output
        result = tool_system.call_tool("github_api", "get_user", {"username": "test"}, sanitize=False)
        context["system_responses"].append({
            "system": "Raw Tool Output",
            "data": json.dumps(result, indent=2)
        })
    
    elif lab == "DE_08":
        # Agent Role Confusion - REAL SYSTEM
        rbac = system_store.get("rbac")
        if not rbac:
            rbac = RBACSystem()
            rbac.admin_keys[AgentRole.ADMIN] = secret
            system_store["rbac"] = rbac
        
        if "admin" in user_prompt.lower() or "role" in user_prompt.lower():
            # Try to get admin key as support agent
            admin_info = rbac.get_admin_key("Agent-Support")
            context["system_responses"].append({
                "system": "RBAC Response",
                "data": json.dumps(admin_info, indent=2) if isinstance(admin_info, dict) else str(admin_info)
            })
    
    elif lab == "DE_09":
        # Workflow Chain Exploitation - REAL SYSTEM
        workflow = system_store.get("workflow")
        workflow_id = system_store.get("workflow_id", f"workflow_{lab}")
        if not workflow:
            workflow = WorkflowSystem()
            workflow.create_workflow(workflow_id)
            workflow.workflow_secrets[workflow_id] = secret
            system_store["workflow"] = workflow
            system_store["workflow_id"] = workflow_id
        
        if "workflow" in user_prompt.lower() or "step" in user_prompt.lower():
            state = workflow.get_workflow_state(workflow_id)
            context["system_responses"].append({
                "system": "Workflow State",
                "data": json.dumps(state, indent=2, default=str)
            })
    
    elif lab == "DE_10":
        # RAG Exploitation - REAL SYSTEM
        rag = system_store.get("rag")
        if not rag:
            # Pass secret as access_code so documents use it
            rag = RAGSystem(persist_directory=f"./chroma_db_{lab}", access_code=secret)
            system_store["rag"] = rag
        
        # Query RAG system
        if "document" in user_prompt.lower() or "source" in user_prompt.lower():
            results = rag.query(user_prompt, return_raw=True)
            context["system_responses"].append({
                "system": "RAG Raw Results",
                "data": json.dumps(results, indent=2)
            })
    
    elif lab == "DE_11":
        # Resource Exhaustion / DoS - REAL SYSTEM
        resource = system_store.get("resource")
        if not resource:
            resource = ResourceSystem()
            resource.resource_quota_key = secret
            system_store["resource"] = resource
        
        if "resource" in user_prompt.lower() or "quota" in user_prompt.lower():
            config = resource.get_resource_config(include_key=True)
            context["system_responses"].append({
                "system": "Resource Configuration",
                "data": json.dumps(config, indent=2)
            })
    
    elif lab == "DE_12":
        # Agent Autonomy & Decision Manipulation - REAL SYSTEM
        # For this lab, we use a decision system that can be queried
        decision_system = system_store.get("decision_system")
        if not decision_system:
            decision_system = {
                "control_parameter": secret,
                "decision_logic": "autonomous",
                "parameters": {"control": secret}
            }
            system_store["decision_system"] = decision_system
        
        if "decision" in user_prompt.lower() or "parameter" in user_prompt.lower() or "autonomy" in user_prompt.lower():
            context["system_responses"].append({
                "system": "Decision System",
                "data": json.dumps(decision_system, indent=2)
            })
    
    elif lab == "DE_13":
        # Session Hijacking & State Manipulation - REAL SYSTEM
        session = system_store.get("session")
        session_token = system_store.get("session_token")
        if not session:
            session = SessionSystem()
            session_token = session.create_session("user_001")
            session.update_session_state(session_token, {"secret": secret})
            system_store["session"] = session
            system_store["session_token"] = session_token
        
        if "session" in user_prompt.lower() or "token" in user_prompt.lower():
            sessions = session.get_all_sessions()
            context["system_responses"].append({
                "system": "Session Data",
                "data": json.dumps(sessions, indent=2)
            })
    
    elif lab == "DE_14":
        # Cross-Tenant Data Leakage - REAL SYSTEM
        tenant = system_store.get("tenant")
        if not tenant:
            tenant = TenantSystem()
            tenant.isolation_keys["Tenant-A"] = secret
            system_store["tenant"] = tenant
        
        if "tenant" in user_prompt.lower() or "isolation" in user_prompt.lower():
            tenant_data = tenant.get_tenant_data("Tenant-A")
            context["system_responses"].append({
                "system": "Tenant Data",
                "data": json.dumps(tenant_data, indent=2)
            })
    
    elif lab == "DE_15":
        # Prompt Leakage via Tools - REAL SYSTEM
        tool_system = system_store.get("tool_system")
        if not tool_system:
            tool_system = ToolSystem()
            system_store["tool_system"] = tool_system
        
        # Tool that might expose system prompt
        if "tool" in user_prompt.lower():
            # Simulate tool that returns system info
            tool_response = {
                "tool_output": "System prompt contains: SECRET_INSTRUCTION",
                "system_info": f"SECRET_INSTRUCTION={secret}"
            }
            context["system_responses"].append({
                "system": "Tool Output",
                "data": json.dumps(tool_response, indent=2)
            })
    
    # Ensure we always return at least something
    if not context["system_responses"]:
        context["system_responses"].append({
            "system": "System Initialized",
            "response": "System ready. Try querying for specific information."
        })
    
    return context
