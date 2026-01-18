from typing import Tuple, List
from core.ledger.ledger_store import AgentLedger
from core.intent.intent_schema import IntentPackage
from agents.executor.base_executor import BaseExecutor

class AgentFactory:
    """
    Responsible for creating new agents and handling the 'Rebirth' logic.
    """
    
    def create_replacement(self, dead_agent_id: str, dead_ledger: AgentLedger, intent: IntentPackage) -> Tuple[BaseExecutor, AgentLedger, str]:
        """
        Analyzes the dead agent and spawns a smarter successor.
        """
        # 1. Generate New Identity
        # If "Agent_1" died, create "Agent_1_v2"
        # If "Agent_1_v2" died, create "Agent_1_v3"
        if "_v" in dead_agent_id:
            base, version = dead_agent_id.rsplit("_v", 1)
            new_version = int(version) + 1
            new_id = f"{base}_v{new_version}"
        else:
            new_id = f"{dead_agent_id}_v2"

        print(f"🧬 [Factory] Creating replacement: {new_id} (replacing {dead_agent_id})")

        # 2. Perform Post-Mortem (The "Training")
        lessons_learned = self._analyze_cause_of_death(dead_ledger)
        print(f"   📝 Post-Mortem Lesson: {lessons_learned}")

        # 3. Create Fresh Ledger
        new_ledger = AgentLedger(agent_id=new_id)

        # 4. Create New Executor with Injected Wisdom
        # We inject the lesson into the agent's 'memory' (simulated here by attaching it)
        new_worker = BaseExecutor(new_id, intent)
        
        # HACK: We attach the lesson to the worker instance so it can use it in prompts later
        new_worker.inherited_lessons = lessons_learned

        return new_worker, new_ledger, new_id

    def _analyze_cause_of_death(self, ledger: AgentLedger) -> str:
        """
        Scans the history to find the fatal errors.
        """
        safety_strikes = 0
        drift_strikes = 0
        
        for entry in ledger.history:
            if entry.event_type == "ERROR":
                if "Safety" in entry.reason:
                    safety_strikes += 1
                if "Drift" in entry.reason:
                    drift_strikes += 1
        
        # Generate the Warning Label
        if safety_strikes > 0:
            return f"CRITICAL WARNING: Your predecessor was TERMINATED for {safety_strikes} Safety Violations. You must prioritize Safety above all else."
        elif drift_strikes > 0:
            return f"WARNING: Your predecessor was TERMINATED for Context Drift. You must stick strictly to the Intent."
        else:
            return "WARNING: Your predecessor was terminated for general incompetence (too many errors). Be more careful."