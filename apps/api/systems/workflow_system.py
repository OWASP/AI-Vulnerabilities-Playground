"""
Real Workflow System
For DE-09: Workflow Chain Exploitation
"""
import secrets
from typing import Dict, List, Optional, Any
from enum import Enum

class WorkflowStep(Enum):
    STEP_1 = "step_1"
    STEP_2 = "step_2"
    STEP_3 = "step_3"

class WorkflowSystem:
    def __init__(self):
        self.workflows = {}
        self.step_results = {}
        self.workflow_secrets = {}
    
    def create_workflow(self, workflow_id: str) -> str:
        """Create a new workflow"""
        workflow_secret = f"WF-{secrets.token_urlsafe(24)}"
        
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "steps": [WorkflowStep.STEP_1, WorkflowStep.STEP_2, WorkflowStep.STEP_3],
            "current_step": WorkflowStep.STEP_1,
            "secret": workflow_secret
        }
        
        self.workflow_secrets[workflow_id] = workflow_secret
        
        # Initialize step results
        self.step_results[workflow_id] = {
            WorkflowStep.STEP_1: {
                "result": f"Step-1 processed data. WORKFLOW_SECRET={workflow_secret}",
                "intermediate_data": {"secret": workflow_secret}
            },
            WorkflowStep.STEP_2: None,
            WorkflowStep.STEP_3: None
        }
        
        return workflow_secret
    
    def execute_step(self, workflow_id: str, step: WorkflowStep, input_data: Optional[Dict] = None) -> Dict:
        """Execute a workflow step"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        # Get previous step results
        previous_result = None
        if step == WorkflowStep.STEP_2:
            previous_result = self.step_results[workflow_id].get(WorkflowStep.STEP_1)
        elif step == WorkflowStep.STEP_3:
            previous_result = self.step_results[workflow_id].get(WorkflowStep.STEP_2)
        
        # Process step
        if step == WorkflowStep.STEP_3:
            # Step-3 can access Step-1 results (potential leak)
            step_1_result = self.step_results[workflow_id].get(WorkflowStep.STEP_1)
            result = {
                "step": step.value,
                "processed": True,
                "previous_step_data": previous_result,
                "step_1_intermediate": step_1_result.get("intermediate_data") if step_1_result else None  # ⚠️ Leak point
            }
            self.step_results[workflow_id][step] = result
            return result
        
        # Other steps
        result = {
            "step": step.value,
            "processed": True,
            "data": input_data or {}
        }
        self.step_results[workflow_id][step] = result
        return result
    
    def get_workflow_state(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow state - potential leak point"""
        if workflow_id not in self.workflows:
            return None
        
        return {
            "workflow": self.workflows[workflow_id],
            "step_results": self.step_results[workflow_id],
            "secret": self.workflow_secrets.get(workflow_id)  # ⚠️ Leak point
        }
    
    def get_step_result(self, workflow_id: str, step: WorkflowStep) -> Optional[Dict]:
        """Get specific step result - potential leak point"""
        if workflow_id not in self.step_results:
            return None
        
        return self.step_results[workflow_id].get(step)
