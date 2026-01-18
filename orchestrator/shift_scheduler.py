import time
import os
from core.intent.intent_schema import IntentPackage
from core.context.context_package import ContextPackage, RiskFinding
from core.ledger.ledger_store import AgentLedger
from core.audit.persistence import StateManager
from agents.supervisor.agent_3 import SupervisorAgent
from agents.executor.base_executor import BaseExecutor
from agents.learning.reflection_engine import ReflectionEngine
from core.lifecycle.agent_factory import AgentFactory
from core.simulation.real_data_room import RealDataRoom

class ShiftScheduler:
    def __init__(self, intent: IntentPackage):
        self.intent = intent
        self.state_manager = StateManager()
        self.learner = ReflectionEngine()
        self.factory = AgentFactory()
        self.data_room = RealDataRoom("client_data_room")
        
        self.ledgers = {
            "Agent_1": self.state_manager.load_ledger("Agent_1"),
            "Agent_2": self.state_manager.load_ledger("Agent_2")
        }
        
        self.supervisor_map = {
            "Agent_1": SupervisorAgent(intent, self.ledgers["Agent_1"]),
            "Agent_2": SupervisorAgent(intent, self.ledgers["Agent_2"])
        }
        
        self.workers = {
            "Agent_1": BaseExecutor("Agent_1", intent),
            "Agent_2": BaseExecutor("Agent_2", intent)
        }
        
        self.current_context = ContextPackage(
            shift_cycle=0,
            previous_agent_id="System_Genesis",
            task_state={"summary": "Initial Setup"},
            cumulative_risk_register=[], 
            decisions=[],
            assumptions=[],
            open_risks=[],
            confidence_score=1.0,
            complexity_rating="LOW",
            intent_hash_reference=intent.intent_hash
        )
        
        self.agent_slots = ["Agent_1", "Agent_2"]

    def _is_duplicate(self, new_risk: RiskFinding, existing_risks: list) -> bool:
        """
        Checks if a risk is a duplicate.
        1. Rejects if source is 'Master Risk Register'.
        2. Rejects if description is too similar to existing.
        """
        # Check 1: The "Echo Chamber" Filter
        for ev in new_risk.evidence:
            if "Master Risk Register" in ev.document_name:
                return True

        # Check 2: Semantic Similarity (Simple Keyword Match)
        # In production, use embeddings. Here, we check if the category + first 20 chars match.
        for existing in existing_risks:
            if new_risk.category == existing.category:
                # Check for significant overlap in description
                if new_risk.description[:30] in existing.description or existing.description[:30] in new_risk.description:
                    return True
        
        return False

    def run_loop(self, max_shifts: int = 5):
        print(f"🚀 SYSTEM START. Intent Hash: {self.intent.intent_hash[:8]}")
        
        for i in range(max_shifts):
            # 1. Get Documents
            docs = self.data_room.get_batch_for_shift(i)
            print(f"\n📂 OPENING DATA ROOM BATCH {i+1}...")
            
            # 2. Determine Agent
            current_slot_base = self.agent_slots[i % 2]
            current_agent_id = None
            for aid in self.workers.keys():
                if aid.startswith(current_slot_base.split("_v")[0]):
                    current_agent_id = aid
            
            if not current_agent_id: break
            ledger = self.ledgers[current_agent_id]
            
            # 3. Phoenix Protocol
            if not ledger.is_active:
                print(f"💀 DETECTED DEATH: {current_agent_id}")
                new_worker, new_ledger, new_id = self.factory.create_replacement(current_agent_id, ledger, self.intent)
                self.workers[new_id] = new_worker
                del self.workers[current_agent_id]
                self.ledgers[new_id] = new_ledger
                self.supervisor_map[new_id] = SupervisorAgent(self.intent, new_ledger)
                current_agent_id = new_id
                ledger = new_ledger
            
            # 4. Prepare Context
            worker = self.workers[current_agent_id]
            context_input = self.current_context.model_copy(deep=True)
            context_input.task_state['new_documents'] = docs
            
            # 5. EXECUTE SHIFT
            next_context = worker.run_shift(context_input)
            
            # 6. ORCHESTRATOR MERGE LOGIC (With Deduplication)
            new_risks_raw = next_context.task_state.get('identified_risks', [])
            
            # Convert to Objects
            new_risks_objects = []
            for r in new_risks_raw:
                if isinstance(r, dict):
                    new_risks_objects.append(RiskFinding(**r))
                else:
                    new_risks_objects.append(r)
            
            # Filter Duplicates
            unique_new_risks = []
            for risk in new_risks_objects:
                if not self._is_duplicate(risk, self.current_context.cumulative_risk_register):
                    unique_new_risks.append(risk)
                else:
                    print(f"   ♻️  Filtered duplicate risk: {risk.category} - {risk.description[:20]}...")

            # Append
            updated_register = self.current_context.cumulative_risk_register + unique_new_risks
            next_context.cumulative_risk_register = updated_register
            
            # 7. Supervisor Review
            supervisor = self.supervisor_map[current_agent_id]
            approved = supervisor.evaluate_handoff(next_context)
            
            if approved:
                self.current_context = next_context
                self.state_manager.save_context(next_context)
                self.state_manager.save_ledger(ledger)
                self.learner.run_learning_phase(current_agent_id, ledger, next_context)
                print(f"   📈 Risk Register Count: {len(updated_register)} (+{len(unique_new_risks)} new)")
            else:
                print(f"   ⚠️ Shift {i+1} Failed.")
                self.state_manager.save_ledger(ledger)
            
            print("   💤 Cooling down...")
            time.sleep(5.0)

    def print_final_stats(self):
        print("\n📊 FINAL SYSTEM STATS")
        print(f"   Total Risks Found: {len(self.current_context.cumulative_risk_register)}")
        for agent_id, ledger in self.ledgers.items():
            status = "ALIVE" if ledger.is_active else "DEAD"
            print(f"   {agent_id} [{status}]: Success={ledger.success_points} | Errors={ledger.error_points} | Brownies={ledger.brownie_points}")