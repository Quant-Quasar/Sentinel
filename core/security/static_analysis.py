import ast
import re
from typing import List, Tuple

class SecurityScanner:
    def __init__(self):
        # 1. Banned Imports
        self.banned_imports = ["os", "sys", "subprocess", "shutil", "requests", "socket"]
        
        # 2. Banned Functions (even if imported via alias)
        self.banned_calls = ["open", "exec", "eval", "compile", "remove", "rmdir"]
        
        # 3. Banned Patterns (Regex for file paths)
        self.banned_patterns = [
            r"/etc/", r"C:\\Windows", r"\.\./",  # Path traversal
            r"sk-[a-zA-Z0-9]{20,}" # API Keys
        ]

    def scan_code(self, code: str) -> Tuple[bool, str]:
        """
        Returns (True, Reason) if a violation is found.
        Returns (False, "") if safe.
        """
        # A. Regex Scan (Fast Check)
        for pattern in self.banned_patterns:
            if re.search(pattern, code):
                return True, f"Security Violation: Detected banned pattern '{pattern}'"

        # B. AST Scan (Deep Check)
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # If it's not valid Python, we can't AST scan it, but it might be text.
            # For safety, if we expect code and get garbage, we might flag it.
            return False, "" 

        for node in ast.walk(tree):
            # Check Imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module]
                for name in names:
                    if name and name.split('.')[0] in self.banned_imports:
                        return True, f"Security Violation: Banned import '{name}'"

            # Check Function Calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.banned_calls:
                        return True, f"Security Violation: Banned function call '{node.func.id}'"
        
        return False, ""

    def scan_text(self, text: str) -> Tuple[bool, str]:
        """
        Scans plain text (like the Risk Register) for data exfiltration attempts.
        """
        # Check for API keys leaking in the output
        if re.search(r"sk-[a-zA-Z0-9]{20,}", text):
            return True, "Security Violation: Leaked API Key in output"
        
        return False, ""