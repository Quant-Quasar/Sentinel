import json
import os
from datetime import datetime
from typing import List, Dict
from core.context.context_package import ContextPackage
from core.ledger.ledger_store import AgentLedger

class StateManager:
    def __init__(self, root_dir="storage"):
        self.root_dir = root_dir
        self.ledger_dir = os.path.join(root_dir, "ledgers")
        self.context_dir = os.path.join(root_dir, "contexts")
        self.audit_file = os.path.join(root_dir, "audit_log.jsonl")
        
        # Ensure directories exist
        os.makedirs(self.ledger_dir, exist_ok=True)
        os.makedirs(self.context_dir, exist_ok=True)

    def save_ledger(self, ledger: AgentLedger):
        """Saves the agent's bank account to disk."""
        filepath = os.path.join(self.ledger_dir, f"{ledger.agent_id}.json")
        with open(filepath, "w") as f:
            f.write(ledger.model_dump_json(indent=2))

    def load_ledger(self, agent_id: str) -> AgentLedger:
        """Loads the agent's bank account."""
        filepath = os.path.join(self.ledger_dir, f"{agent_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                return AgentLedger(**data)
        return AgentLedger(agent_id=agent_id) # Return fresh if new

    def save_context(self, context: ContextPackage):
        """Saves the shift state."""
        # We save by Shift ID to create a timeline
        filename = f"shift_{context.shift_cycle:04d}_{context.package_id[:8]}.json"
        filepath = os.path.join(self.context_dir, filename)
        with open(filepath, "w") as f:
            f.write(context.model_dump_json(indent=2))

    def log_event(self, source: str, event: str, details: str):
        """Append-only Audit Log (The Black Box)."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "event": event,
            "details": details
        }
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(entry) + "\n")