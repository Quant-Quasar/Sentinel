from core.intent.intent_schema import IntentPackage

def test_intent_security():
    print("🔒 Testing Intent Security...")

    # 1. Create the Intent
    intent = IntentPackage(
        original_prompt="Build a website",
        constraints=["Use React"],
        prohibited_actions=["No SQL Injection"],
        success_definition="It loads."
    )
    
    # 2. Sign it (Lock it)
    intent.sign()
    print(f"✅ Intent Signed. Hash: {intent.intent_hash}")

    # 3. Verify Integrity (Should Pass)
    if intent.validate_integrity():
        print("✅ Integrity Check Passed: Data is pristine.")
    else:
        print("❌ Integrity Check Failed!")

    # 4. Simulate an Attack (Tampering)
    print("\n🕵️  Simulating Malicious Agent Attack...")
    # The agent tries to remove a constraint
    intent.constraints = [] 
    
    # 5. Verify Integrity (Should Fail)
    if intent.validate_integrity():
        print("❌ SECURITY HOLE: Tampering went undetected!")
    else:
        print("✅ ATTACK BLOCKED: Hash mismatch detected.")
        print(f"   Stored Hash:  {intent.intent_hash}")
        print(f"   Actual Hash:  {intent.compute_hash()}")

if __name__ == "__main__":
    test_intent_security()