from core.context.context_package import ContextPackage
from pydantic import ValidationError

def test_context_structure():
    print("📦 Testing Context Structure...")

    try:
        # 1. Create a Valid Package
        ctx = ContextPackage(
            shift_cycle=1,
            previous_agent_id="Agent_Alpha",
            task_state={"status": "drafting", "code": "print('hello')"},
            decisions=["Selected Python"],
            assumptions=["User has Python installed"],
            confidence_score=0.95,
            intent_hash_reference="abc123hash"
        )
        print(f"✅ Valid Package Created:\n{ctx.summary()}")

    except ValidationError as e:
        print(f"❌ Unexpected Error: {e}")

    # 2. Test Validation Logic (Invalid Confidence)
    print("\n🧪 Testing Validation Logic...")
    try:
        bad_ctx = ContextPackage(
            shift_cycle=1,
            previous_agent_id="Agent_Beta",
            task_state={},
            confidence_score=1.5, # This is invalid (must be 0-1)
            intent_hash_reference="abc123hash"
        )
        print("❌ FAILED: System accepted invalid confidence score!")
    except ValidationError as e:
        print("✅ SUCCESS: System rejected invalid confidence score.")
        # print(e) # Uncomment to see the error message

if __name__ == "__main__":
    test_context_structure()