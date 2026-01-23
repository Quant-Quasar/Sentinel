from core.intent.intent_schema import IntentPackage
from orchestrator.shift_scheduler import ShiftScheduler
import os
import shutil

def main():
    # 1. Clean Start
    if os.path.exists("storage"):
        shutil.rmtree("storage")
        print("🧹 Storage wiped for Blind Test.")

    print("🔌 SYSTEM ONLINE. MODE: BLIND FORENSIC AUDIT")
    
    # 2. Define a GENERIC Intent (Simulating a lazy client)
    intent = IntentPackage(
        original_prompt="Perform a full Due Diligence review on LogiFlow Technologies.",
        constraints=[
            "Identify all material Legal, Financial, and Commercial risks.",
            "Focus on issues that would affect the valuation or deal structure.",
            "Must cite page numbers for every finding."
        ],
        prohibited_actions=[
            "Do not summarize without citation.",
            "Do not use vague qualifiers (e.g., 'huge', 'tiny'). Use numbers."
        ],
        success_definition="A comprehensive Risk Register covering all standard M&A risk categories."
    )
    intent.sign()

    # 3. Initialize Scheduler
    scheduler = ShiftScheduler(intent)
    
    # 4. Run
    total_docs = scheduler.data_room.get_total_docs()
    if total_docs == 0:
        print("❌ No documents found.")
        return

    print(f"🚀 Starting Analysis of {total_docs} documents...")
    scheduler.run_loop(max_shifts=total_docs + 1)
    scheduler.print_final_stats()

if __name__ == "__main__":
    main()