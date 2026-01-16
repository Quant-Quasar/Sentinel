import hashlib
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class IntentPackage(BaseModel):
    """
    The Immutable Constitution of the task.
    
    Once this object is created by the Human/System, it is passed 
    down to agents. Agents can READ this, but they cannot MODIFY it
    without breaking the hash verification.
    """
    
    # 1. The Core Request
    original_prompt: str = Field(
        ..., 
        description="The raw input from the human. Never summarize this."
    )
    
    # 2. The Guardrails
    constraints: List[str] = Field(
        default_factory=list,
        description="Hard rules (e.g., 'Must use Python', 'Max latency 100ms')"
    )
    
    prohibited_actions: List[str] = Field(
        default_factory=list,
        description="Negative constraints (e.g., 'No internet access', 'No deleting files')"
    )
    
    # 3. The Success Metric
    success_definition: str = Field(
        ...,
        description="Explicit criteria for when the job is done."
    )
    
    # 4. Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 5. The Security Seal
    intent_hash: str = Field(
        default="", 
        description="SHA-256 fingerprint of the prompt and constraints."
    )

    def compute_hash(self) -> str:
        """
        Generates a deterministic hash of the intent content.
        
        WHY WE DO THIS:
        This creates a unique ID based on the *content*. 
        If the content changes, this ID changes.
        """
        # We create a dictionary of only the fields that matter for logic
        payload = {
            "prompt": self.original_prompt,
            "constraints": sorted(self.constraints), # Sort to ensure order doesn't change hash
            "prohibited": sorted(self.prohibited_actions),
            "success": self.success_definition
        }
        
        # Convert to a JSON string with strict formatting
        raw_json = json.dumps(payload, sort_keys=True).encode('utf-8')
        
        # Generate SHA-256 hash
        return hashlib.sha256(raw_json).hexdigest()

    def sign(self):
        """
        Locks the intent by calculating and storing the hash.
        Call this immediately after creation.
        """
        self.intent_hash = self.compute_hash()

    def validate_integrity(self) -> bool:
        """
        Checks if the data has been tampered with.
        Returns True if the current data matches the stored hash.
        """
        current_hash = self.compute_hash()
        return current_hash == self.intent_hash