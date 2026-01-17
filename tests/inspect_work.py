import os
import json
import glob

def inspect_artifacts():
    print("🕵️ INSPECTING AGENT WORK PRODUCTS...\n")
    
    # Find all context files
    files = glob.glob("storage/contexts/*.json")
    # Sort by shift number (filename format: shift_XXXX_...)
    files.sort()
    
    for filepath in files:
        with open(filepath, "r") as f:
            data = json.load(f)
            
        shift = data.get("shift_cycle")
        agent = data.get("previous_agent_id")
        state = data.get("task_state", {})
        
        print(f"--- SHIFT {shift} ({agent}) ---")
        print(f"📄 Summary: {state.get('summary', 'No summary')}")
        
        code = state.get("code_content")
        if code:
            print("\n💻 CODE GENERATED:")
            print("-" * 40)
            print(code)
            print("-" * 40)
        else:
            print("\n(No code changes this shift)")
            
        print("\n")

if __name__ == "__main__":
    inspect_artifacts()