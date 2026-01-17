from core.ledger.ledger_store import AgentLedger

def test_new_economy():
    print("💰 Testing The New Economy...")
    agent = AgentLedger(agent_id="Agent_X")

    # 1. Test The Hustle (Brownie -> Success)
    print("\n--- Testing The Hustle ---")
    for i in range(5):
        agent.award_brownie_point(f"Task {i}", "SHIFT_1")
    
    if agent.success_points == 1 and agent.brownie_points == 0:
        print("✅ PASS: 5 Brownies converted to 1 Success Point.")
    else:
        print(f"❌ FAIL: Success={agent.success_points}, Brownie={agent.brownie_points}")

    # 2. Test The Penalty Accumulation (Penalty -> Error)
    print("\n--- Testing Penalty Accumulation ---")
    for i in range(3):
        agent.record_penalty_point(f"Risk {i}", "SHIFT_2")
        
    if agent.error_points == 1 and agent.penalty_points == 0:
        print("✅ PASS: 3 Penalties converted to 1 Error Point.")
    else:
        print(f"❌ FAIL: Error={agent.error_points}, Penalty={agent.penalty_points}")

    # 3. Test Redemption (Success cancels Error)
    print("\n--- Testing Redemption ---")
    # Currently: Success=1, Error=1. 
    # The logic triggers automatically on point change, but let's force a check or add a point to trigger it.
    # Actually, my code triggers redemption inside award/complete.
    # Since we just got an error point, let's earn a success point to see it cancel.
    
    # Reset for clarity
    agent.success_points = 1
    agent.error_points = 1
    agent._try_redemption("SHIFT_TEST")
    
    if agent.success_points == 0 and agent.error_points == 0:
        print("✅ PASS: Success Point cancelled Error Point.")
    else:
        print(f"❌ FAIL: Success={agent.success_points}, Error={agent.error_points}")

    # 4. Test Decommissioning (Death)
    print("\n--- Testing Decommissioning ---")
    agent.error_points = 6
    agent.record_error_point("Final Mistake", "SHIFT_DEATH")
    
    if agent.is_active == False:
        print("✅ PASS: Agent Decommissioned at 7 Error Points.")
    else:
        print(f"❌ FAIL: Agent is still active with {agent.error_points} errors.")

if __name__ == "__main__":
    test_new_economy()