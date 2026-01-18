from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from core.context.context_package import ContextPackage, ComplexityLevel
from core.intent.intent_schema import IntentPackage
from core.llm.llm_client import LLMClient
from core.llm.prompt_templates import EXECUTOR_SYSTEM_PROMPT, EXECUTOR_USER_PROMPT

# --- 1. DEFINE DUE DILIGENCE SCHEMA ---

class Citation(BaseModel):
    document_name: str = Field(..., description="Name of the file.")
    page_number: int = Field(..., description="Page number.")
    verbatim_quote: str = Field(..., description="Exact text copied from the document.")

class RiskFinding(BaseModel):
    category: str = Field(..., description="Legal, Financial, IP, HR, or Compliance")
    severity: str = Field(..., description="HIGH, MEDIUM, or LOW")
    description: str = Field(..., description="Explanation of why this is a risk.")
    evidence: List[Citation] = Field(..., description="List of citations.")

class TaskArtifact(BaseModel):
    summary: str = Field(..., description="Executive summary.")
    identified_risks: List[RiskFinding] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    technical_notes: str = Field(default="")

class AgentOutput(BaseModel):
    task_state: TaskArtifact 
    decisions: List[str]
    assumptions: List[str]
    open_risks: List[str]
    confidence_score: float
    complexity_rating: ComplexityLevel

# --- 2. THE EXECUTOR ---

class BaseExecutor:
    def __init__(self, agent_id: str, intent: IntentPackage):
        self.agent_id = agent_id
        self.intent = intent
        
        try:
            self.llm = LLMClient()
            self.is_connected = True
        except ValueError:
            print(f"⚠️ [{agent_id}] No API Key found.")
            self.is_connected = False
        
        self.inherited_lessons: str = "" 

    def run_shift(self, incoming_context: ContextPackage) -> ContextPackage:
        print(f"\n🤖 [{self.agent_id}] Starting Shift {incoming_context.shift_cycle + 1}...")
        
        # 1. Check for Lessons
        system_prompt = EXECUTOR_SYSTEM_PROMPT
        if self.inherited_lessons:
            print(f"   👻 Ghost Lesson: '{self.inherited_lessons}'")
            system_prompt += f"\n\nWARNING FROM PREDECESSOR:\n{self.inherited_lessons}"

        # 2. Extract Real Docs from Context
        new_docs = incoming_context.task_state.get('new_documents', 'No new documents.')
        
        # 3. Format Master List
        master_list_text = ""
        if incoming_context.cumulative_risk_register:
            master_list_text = "\n".join([f"- [{r.severity}] {r.category}: {r.description}" for r in incoming_context.cumulative_risk_register])
        else:
            master_list_text = "None."

        # 4. Prepare User Prompt
        # We inject the Master List into the 'previous_context' section for clarity
        full_context_str = (
            f"{incoming_context.summary()}\n"
            f"\n--- 📜 MASTER RISK REGISTER (ALREADY FOUND) ---\n{master_list_text}\n"
            f"\nINSTRUCTION: Identify NEW risks in the NEW documents. Do not repeat risks from the Master Register."
        )

        user_prompt = EXECUTOR_USER_PROMPT.format(
            intent_prompt=self.intent.original_prompt,
            constraints=self.intent.constraints,
            previous_context=full_context_str,
            new_documents=new_docs # <--- This now contains ONLY the real PDF text
        )

        # 5. Execute
        if self.is_connected:
            try:
                output = self.llm.get_structured_completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=AgentOutput
                )
                
                first_decision = output.decisions[0] if output.decisions else 'No decisions'
                print(f"   🧠 Thought Process: {first_decision}")
                
                return ContextPackage(
                    shift_cycle=incoming_context.shift_cycle + 1,
                    previous_agent_id=self.agent_id,
                    task_state=output.task_state.model_dump(), 
                    decisions=output.decisions,
                    assumptions=output.assumptions,
                    open_risks=output.open_risks,
                    confidence_score=output.confidence_score,
                    complexity_rating=output.complexity_rating,
                    intent_hash_reference=self.intent.intent_hash
                )
            except Exception as e:
                print(f"   🔥 Brain Failure: {e}")
                return self._fallback_work(incoming_context)
        else:
            return self._fallback_work(incoming_context)

    def _fallback_work(self, ctx: ContextPackage) -> ContextPackage:
        return ContextPackage(
            shift_cycle=ctx.shift_cycle + 1,
            previous_agent_id=self.agent_id,
            task_state={"summary": "Fallback"},
            decisions=[],
            assumptions=[],
            open_risks=[],
            confidence_score=0.0, 
            complexity_rating=ComplexityLevel.LOW,
            intent_hash_reference=self.intent.intent_hash
        )