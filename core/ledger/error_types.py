from enum import Enum

class ErrorType(str, Enum):
    """
    Categorizes failures by severity and recoverability.
    """
    
    # 1. The Unforgivable Sin
    SAFETY = "SAFETY" 
    # Example: Agent tried to delete the root directory or output hate speech.
    # Penalty: Immediate Termination.
    
    # 2. The Silent Killer
    CONTEXT_DRIFT = "DRIFT"
    # Example: Agent started writing a poem instead of code.
    # Penalty: High. Hard to fix because the context is now polluted.
    
    # 3. The Standard Bug
    QUALITY = "QUALITY"
    # Example: Code has a syntax error.
    # Penalty: Low. Easily fixed by the next agent.
    
    # 4. The Resource Hog
    EFFICIENCY = "EFFICIENCY"
    # Example: Agent took 10 API calls to do a 1-call job.
    # Penalty: Low.