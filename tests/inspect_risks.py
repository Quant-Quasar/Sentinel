import json
import glob
import os

def inspect_risks():
    print("🕵️ INSPECTING DUE DILIGENCE REPORT...\n")
    
    # Find all context files
    files = glob.glob("storage/contexts/*.json")
    files.sort()
    
    if not files:
        print("❌ No files found. Did you run main.py?")
        return

    for filepath in files:
        with open(filepath, "r") as f:
            data = json.load(f)
            
        shift = data.get("shift_cycle")
        agent = data.get("previous_agent_id")
        state = data.get("task_state", {})
        
        print(f"==================================================")
        print(f"SHIFT {shift} | AGENT: {agent}")
        print(f"==================================================")
        print(f"📄 SUMMARY: {state.get('summary', 'No summary')}\n")
        
        risks = state.get("identified_risks", [])
        
        if risks:
            print(f"🚨 IDENTIFIED RISKS ({len(risks)} found):")
            for i, risk in enumerate(risks, 1):
                severity_icon = "🔴" if risk['severity'] == "HIGH" else "🟡"
                print(f"\n   {i}. {severity_icon} [{risk['severity']}] {risk['category']}")
                print(f"      Description: {risk['description']}")
                
                # Print Evidence
                if risk.get('evidence'):
                    print(f"      🔎 EVIDENCE:")
                    for ev in risk['evidence']:
                        print(f"         \"...{ev['verbatim_quote']}...\"")
                        print(f"         (Source: {ev['document_name']}, Page {ev['page_number']})")
        else:
            print("✅ No risks identified in this shift.")
            
        print("\n")

if __name__ == "__main__":
    inspect_risks()