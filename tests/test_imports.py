import sys
import os

# Add root to python path
sys.path.append(os.getcwd())

def test_structure():
    try:
        import core.intent
        import core.ledger
        import agents.supervisor
        import orchestrator
        print("✅ SUCCESS: System structure is valid and importable.")
    except ImportError as e:
        print(f"❌ FAILURE: {e}")

if __name__ == "__main__":
    test_structure()