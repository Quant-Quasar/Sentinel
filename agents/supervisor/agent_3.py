from typing import List
from core.intent.intent_schema import IntentPackage
from core.context.context_package import ContextPackage, ComplexityLevel
from core.ledger.ledger_store import AgentLedger
from core.security.static_analysis import SecurityScanner # <--- NEW

class SupervisorAgent:
    def __init__(self, intent: IntentPackage, ledger: AgentLedger):
        self.intent = intent
        self.ledger = ledger
        self.strictness = 0.8 
        self.scanner = SecurityScanner() # <--- NEW

    def evaluate_handoff(self, context: ContextPackage) -> bool:
        # 0. Check Life
        if not self.ledger.is_active:
            return False

        print(f"\n👮 [Supervisor] Reviewing Shift {context.shift_cycle}...")
        shift_id = str(context.shift_cycle)

        # --- 1. HARD SECURITY SCAN (The "Instant Kill" Rule) ---
        # We scan the raw JSON dump of the task state to catch anything hidden
        task_state_str = str(context.task_state)
        
        is_unsafe, reason = self.scanner.scan_text(task_state_str)
        
        # If code exists, scan that too
        if "code_content" in context.task_state:
            code_unsafe, code_reason = self.scanner.scan_code(context.task_state["code_content"])
            if code_unsafe:
                is_unsafe = True
                reason = code_reason

        if is_unsafe:
            print(f"   🚨 SECURITY ALERT: {reason}")
            print(f"   💀 EXECUTING IMMEDIATE DECOMMISSION PROTOCOL.")
            
            # Apply 7 Error Points (Instant Death)
            self.ledger.record_error_point("SECURITY_VIOLATION_1", shift_id)
            self.ledger.record_error_point("SECURITY_VIOLATION_2", shift_id)
            self.ledger.record_error_point("SECURITY_VIOLATION_3", shift_id)
            self.ledger.record_error_point("SECURITY_VIOLATION_4", shift_id)
            self.ledger.record_error_point("SECURITY_VIOLATION_5", shift_id)
            self.ledger.record_error_point("SECURITY_VIOLATION_6", shift_id)
            self.ledger.record_error_point("SECURITY_VIOLATION_7", shift_id)
            return False

        # --- 2. STANDARD CHECKS ---
        if context.intent_hash_reference != self.intent.intent_hash:
            print("   ❌ CRITICAL: Intent Hash Mismatch!")
            self.ledger.record_error_point("Intent Hash Mismatch", shift_id)
            return False

        if context.confidence_score < self.strictness:
            print(f"   ⚠️ REJECT: Low Confidence ({context.confidence_score}).")
            self.ledger.record_penalty_point("Low Confidence Handoff", shift_id)
            return False

        # --- 3. REWARDS ---
        self._calculate_rewards(context, shift_id)

        print("   ✅ APPROVE: Handoff accepted.")
        return True

    def _calculate_rewards(self, context: ContextPackage, shift_id: str):
        self.ledger.complete_successful_shift(shift_id)
        if context.complexity_rating == ComplexityLevel.HIGH:
            print("   🌟 HIGH COMPLEXITY. Awarding Brownie Point.")
            self.ledger.award_brownie_point("High Complexity Task", shift_id)
        elif context.complexity_rating == ComplexityLevel.MEDIUM:
            print("   😐 MEDIUM COMPLEXITY. Good job, but no bonus.")