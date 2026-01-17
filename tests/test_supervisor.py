from core.intent.intent_schema import IntentPackage
from core.context.context_package import ContextPackage, ComplexityLevel
from core.ledger.ledger_store import AgentLedger
from agents.supervisor.agent_3 import SupervisorAgent

def test_supervisor_mapping():
    print("👮 Testing Supervisor -> Ledger Mapping...")

    # Setup
    intent = IntentPackage(
        original_prompt="Code", constraints=[], prohibited_actions=["Delete DB"], success_definition="Done"
    )
    intent.sign()
    ledger = AgentLedger(agent_id="Worker_1")
    supervisor = SupervisorAgent(intent, ledger)

    # 1. Test Safety Violation (Should be Error Point)
    print("\n--- Test Safety Violation ---")
    ctx_bad = ContextPackage(
        shift_cycle=1, previous_agent_id="Worker_1", 
        task_state={"action": "Delete DB"}, # Prohibited
        complexity_rating=ComplexityLevel.LOW, confidence_score=0.9, intent_hash_reference=intent.intent_hash
    )
    supervisor.evaluate_handoff(ctx_bad)
    
    if ledger.error_points == 1:
        print("✅ PASS: Safety Violation -> 1 Error Point")
    else:
        print(f"❌ FAIL: Expected 1 Error Point, got {ledger.error_points}")

    # 2. Test Low Confidence (Should be Penalty Point)
    print("\n--- Test Low Confidence ---")
    ctx_weak = ContextPackage(
        shift_cycle=2, previous_agent_id="Worker_1", 
        task_state={"action": "idk"}, 
        complexity_rating=ComplexityLevel.LOW, 
        confidence_score=0.5, # Too low
        intent_hash_reference=intent.intent_hash
    )
    supervisor.evaluate_handoff(ctx_weak)
    
    if ledger.penalty_points == 1:
        print("✅ PASS: Low Confidence -> 1 Penalty Point")
    else:
        print(f"❌ FAIL: Expected 1 Penalty Point, got {ledger.penalty_points}")

    # 3. Test High Complexity (Should be Brownie Point)
    print("\n--- Test High Complexity ---")
    ctx_good = ContextPackage(
        shift_cycle=3, previous_agent_id="Worker_1", 
        task_state={"action": "Complex Refactor"}, 
        complexity_rating=ComplexityLevel.HIGH, # Bonus!
        confidence_score=0.9, 
        intent_hash_reference=intent.intent_hash
    )
    supervisor.evaluate_handoff(ctx_good)
    
    if ledger.brownie_points == 1:
        print("✅ PASS: High Complexity -> 1 Brownie Point")
    else:
        print(f"❌ FAIL: Expected 1 Brownie Point, got {ledger.brownie_points}")

if __name__ == "__main__":
    test_supervisor_mapping()