from typing import List
from core.ledger.ledger_store import AgentLedger
from core.context.context_package import ContextPackage

class ReflectionEngine:
    """
    The 'Sleep' cycle for agents.
    This runs AFTER a shift ends and BEFORE the agent is queued again.
    """
    
    def run_learning_phase(self, agent_id: str, ledger: AgentLedger, recent_context: ContextPackage):
        print(f"\n🧠 [{agent_id}] Entering Learning Phase...")
        
        # 1. Review Penalties
        # In a real system, the LLM would read its own error log here.
        recent_errors = [e for e in ledger.history if e.event_type in ["PENALTY", "ERROR"] and e.related_shift_id == str(recent_context.shift_cycle)]
        
        if recent_errors:
            print(f"   [{agent_id}] Reflecting on {len(recent_errors)} recent errors...")
            for err in recent_errors:
                print(f"      - Acknowledged: {err.reason}")
        else:
            print(f"   [{agent_id}] No recent errors. Consolidating memory.")

        print(f"   [{agent_id}] Memory compressed. Ready for next cycle.")