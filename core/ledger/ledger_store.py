from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from core.ledger.error_types import ErrorType

class LedgerEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str 
    amount: float
    reason: str
    related_shift_id: str

class AgentLedger(BaseModel):
    agent_id: str
    
    # --- THE CURRENCIES ---
    brownie_points: int = 0
    penalty_points: int = 0
    
    # The "Big" Currencies
    success_points: int = 0
    error_points: float = 0.0 # Float to handle partial conversions if needed
    
    # State Tracking
    shift_streak: int = 0
    is_active: bool = True # Alive or Decommissioned
    
    history: List[LedgerEntry] = Field(default_factory=list)

    # --- 1. THE GRIND (Safe Path) ---
    def complete_successful_shift(self, shift_id: str):
        if not self.is_active: return

        self.shift_streak += 1
        self._log("SHIFT_COMPLETE", 0, f"Streak: {self.shift_streak}", shift_id)
        
        # Rule: 7 shifts without error = 1 success point
        if self.shift_streak >= 7:
            self.success_points += 1
            self.shift_streak = 0 # Reset streak after payout
            self._log("MILESTONE", 1, "Earned Success Point (7-Shift Streak)", shift_id)
            print(f"🏆 [{self.agent_id}] +1 Success Point (Grind)")
            self._try_redemption(shift_id)

    # --- 2. THE HUSTLE (Risky Path) ---
    def award_brownie_point(self, reason: str, shift_id: str):
        """Rule: 1 Difficult Task = 1 Brownie Point"""
        if not self.is_active: return

        self.brownie_points += 1
        self._log("REWARD", 1, f"Brownie Point: {reason}", shift_id)
        print(f"🍪 [{self.agent_id}] +1 Brownie Point")
        
        # Rule: 5 Brownie Points = 1 Success Point
        if self.brownie_points >= 5:
            self.brownie_points -= 5
            self.success_points += 1
            self._log("EXCHANGE", 1, "Converted 5 Brownie Points -> 1 Success Point", shift_id)
            print(f"💱 [{self.agent_id}] +1 Success Point (Hustle)")
            self._try_redemption(shift_id)

    # --- 3. THE PENALTIES ---
    def record_penalty_point(self, reason: str, shift_id: str):
        """Rule: Risky behavior/Bad Handoff = 1 Penalty Point"""
        if not self.is_active: return

        self.penalty_points += 1
        self.shift_streak = 0 # Streak broken
        self._log("PENALTY", 1, f"Penalty Point: {reason}", shift_id)
        print(f"⚠️ [{self.agent_id}] +1 Penalty Point")
        
        # Rule: 3 Penalty Points = 1 Error Point
        if self.penalty_points >= 3:
            self.penalty_points -= 3
            self.error_points += 1
            self._log("CONVERSION", 1, "Converted 3 Penalty Points -> 1 Error Point", shift_id)
            print(f"❌ [{self.agent_id}] +1 Error Point (Accumulated Penalties)")
            self._check_termination(shift_id)

    def record_error_point(self, reason: str, shift_id: str):
        """Rule: 1 Error = 1 Error Point"""
        if not self.is_active: return

        self.error_points += 1
        self.shift_streak = 0
        self._log("ERROR", 1, f"Direct Error Point: {reason}", shift_id)
        print(f"🛑 [{self.agent_id}] +1 Error Point (Direct)")
        self._check_termination(shift_id)

    # --- 4. REDEMPTION & DEATH ---
    def _try_redemption(self, shift_id: str):
        """Rule: 1 Success Point cancels 1 Error Point"""
        if self.success_points > 0 and self.error_points > 0:
            self.success_points -= 1
            self.error_points -= 1
            self._log("REDEMPTION", -1, "Used Success Point to cancel Error Point", shift_id)
            print(f"😇 [{self.agent_id}] REDEMPTION! Error Point cancelled.")

    def _check_termination(self, shift_id: str):
        """Rule: 7 Error Points = Decommission"""
        if self.error_points >= 7:
            self.is_active = False
            self._log("TERMINATION", 0, "Reached 7 Error Points", shift_id)
            print(f"💀 [{self.agent_id}] DECOMMISSIONED. Too many errors.")

    def _log(self, event: str, amount: float, reason: str, shift_id: str):
        self.history.append(LedgerEntry(
            event_type=event,
            amount=amount,
            reason=reason,
            related_shift_id=shift_id
        ))