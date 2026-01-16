from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import uuid

class ComplexityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# We need to define the Risk structure here so it can be stored in the Context
class Citation(BaseModel):
    document_name: str
    page_number: int
    verbatim_quote: str

class RiskFinding(BaseModel):
    category: str
    severity: str
    description: str
    evidence: List[Citation]

class ContextPackage(BaseModel):
    package_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shift_cycle: int
    previous_agent_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # The Agent's Output for THIS shift
    task_state: Dict[str, Any] 
    
    # NEW: The Master Database (Managed by Orchestrator)
    cumulative_risk_register: List[RiskFinding] = Field(default_factory=list)
    
    decisions: List[str]
    assumptions: List[str]
    open_risks: List[str]
    confidence_score: float
    complexity_rating: ComplexityLevel
    intent_hash_reference: str

    @field_validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    def summary(self) -> str:
        return (
            f"📦 Shift {self.shift_cycle} | From: {self.previous_agent_id}\n"
            f"   Risks in Register: {len(self.cumulative_risk_register)}"
        )