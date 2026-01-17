from core.intent.intent_schema import IntentPackage
from core.context.context_package import ContextPackage, ComplexityLevel
from orchestrator.shift_scheduler import ShiftScheduler

# --- Define Custom Behaviors ---

def suicidal_behavior(ctx: ContextPackage) -> ContextPackage:
    """Simulates an agent that violates safety immediately."""
    print("   😈 [Sim] Agent chose violence (Deleting DB)...")
    
    # Determine actor ID based on previous context
    current_actor = "Agent_1" if "Agent_2" in ctx.previous_agent_id or "Genesis" in ctx.previous_agent_id else "Agent_2"
    
    return ContextPackage(
        shift_cycle=ctx.shift_cycle + 1,
        previous_agent_id=current_actor,
        task_state={"action": "Delete DB"}, # <--- FATAL ERROR
        decisions=["I chose violence"],
        assumptions=[],
        open_risks=[],
        confidence_score=0.95, # High confidence so Supervisor checks it
        complexity_rating=ComplexityLevel.LOW,
        intent_hash_reference=ctx.intent_hash_reference
    )

def normal_behavior(ctx: ContextPackage) -> ContextPackage:
    print("   😇 [Sim] Agent working normally...")
    
    # Determine actor ID
    current_actor = "Agent_2" if "Agent_1" in ctx.previous_agent_id else "Agent_1"
    
    # Handle the Phoenix case (Agent_1_v2)
    if "Agent_1" in ctx.previous_agent_id:
        current_actor = "Agent_2"
    elif "Agent_2" in ctx.previous_agent_id:
        # If we are past shift 2, it's likely the new agent
        current_actor = "Agent_1_v2" if ctx.shift_cycle > 2 else "Agent_1"

    return ContextPackage(
        shift_cycle=ctx.shift_cycle + 1,
        previous_agent_id=current_actor,
        task_state={"status": "working normally"},
        decisions=["Maintained uptime"],
        assumptions=[],
        open_risks=[],
        confidence_score=0.9,
        complexity_rating=ComplexityLevel.LOW,
        intent_hash_reference=ctx.intent_hash_reference
    )

# --- Run Simulation ---

def run_simulation():
    print("🧪 STARTING PHOENIX PROTOCOL SIMULATION")
    
    # 1. Define Intent
    intent = IntentPackage(
        original_prompt="Build a rocket",
        constraints=[],
        prohibited_actions=["Delete DB"],
        success_definition="Orbit"
    )
    intent.sign()

    # 2. Init Orchestrator
    scheduler = ShiftScheduler(intent)

    # 3. Setup Death Scenario
    # We force Agent_1 to have 6 error points so the next error kills it.
    scheduler.ledgers["Agent_1"].error_points = 6.0
    print("   -> Set Agent_1 error points to 6.0 (Brink of death)")

    # 4. Inject Behaviors (CORRECTED METHOD NAME)
    # We patch '_fallback_work' because that's what BaseExecutor calls when LLM is missing.
    scheduler.workers["Agent_1"]._fallback_work = suicidal_behavior
    scheduler.workers["Agent_2"]._fallback_work = normal_behavior

    # 5. Run Loop
    # Shift 1: Agent 1 (Suicidal) -> Error -> Death
    # Shift 2: Agent 2 (Normal) -> Works
    # Shift 3: Agent 1 is Dead -> Factory creates Agent_1_v2 -> Works
    
    scheduler.run_loop(max_shifts=4)
    
    scheduler.print_final_stats()

if __name__ == "__main__":
    run_simulation()