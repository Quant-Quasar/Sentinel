import os
from pathlib import Path

# The Blueprint
STRUCTURE = [
    "core/config",
    "core/intent",
    "core/context",
    "core/ledger",
    "core/audit",
    "core/llm",
    "agents/executor",
    "agents/supervisor",
    "agents/learning",
    "orchestrator",
    "human_interface/escalation_dashboard",
    "simulations",
    "compliance",
    "tests/unit",
    "tests/integration",
    "tests/chaos",
]

FILES = {
    "README.md": "# Governed Agent Platform (GAP)\n\nSystem-first multi-agent architecture.",
    ".env.example": "OPENAI_API_KEY=sk-...\nANTHROPIC_API_KEY=sk-...",
    "core/config/system.yaml": "# System-wide configuration limits\nmax_shift_duration_hours: 24",
    "core/config/agent_roles.yaml": "# Agent capability definitions",
    "docker-compose.yml": "# Future deployment config",
}

def build_scaffold():
    root = Path(".")
    
    print(f"🚀 Initializing GAP Architecture in {root.absolute()}...")

    # 1. Create Directories and __init__.py
    for folder in STRUCTURE:
        path = root / folder
        path.mkdir(parents=True, exist_ok=True)
        # Create __init__.py to make it a package
        (path / "__init__.py").touch()
        print(f"   ✅ Created: {path}")

    # 2. Create Base Files
    for file_path, content in FILES.items():
        path = root / file_path
        if not path.exists():
            with open(path, "w") as f:
                f.write(content)
            print(f"   📄 Created: {path}")
        else:
            print(f"   ⏩ Skipped: {path} (exists)")

    # 3. Create Root __init__.py
    (root / "__init__.py").touch()
    
    print("\n🎉 Architecture Scaffold Complete.")

if __name__ == "__main__":
    build_scaffold()