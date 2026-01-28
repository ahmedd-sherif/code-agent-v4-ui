import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Setup Context
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))
load_dotenv()

from code_agent.tools import write_code
from code_agent.storage import get_session, list_sessions

def verify_agent_capabilities():
    print("🔍 Starting Agent Capability Verification...")
    
    # 1. Identify the Workspace
    workspaces_dir = ROOT_DIR / "Created Programs"
    calc_path = workspaces_dir / "Advanced Calculator"
    
    if not calc_path.exists():
        print(f"❌ Workspace 'Advanced Calculator' not found at {calc_path}")
        print("   Creating it for the test...")
        calc_path.mkdir(parents=True, exist_ok=True)
    else:
        print(f"✅ Workspace found: {calc_path}")

    # 2. Define the code to be written
    calculator_code = """
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Agent Verified Calc")
    label = tk.Label(root, text="Hello from Code Agent!", font=("Arial", 20))
    label.pack(padx=50, pady=50)
    root.mainloop()

if __name__ == "__main__":
    main()
"""
    
    # 3. Simulate the Agent's Tool Call
    # essentially calling write_code(base_path=..., ...)
    print("🤖 Agent is attempting to write 'agent_calc.py'...")
    
    try:
        # Direct tool usage as the agent would do
        result = write_code(
            filename="agent_calc.py",
            code_content=calculator_code,
            base_path=str(calc_path) # Critical: Isolating to workspace
        )
        print(f"🛠️ Tool Output: {result}")
        
    except Exception as e:
        print(f"❌ Agent failed to write code: {e}")
        return

    # 4. Verification
    expected_file = calc_path / "agent_calc.py"
    if expected_file.exists():
        print(f"✅ SUCCESS: File created at {expected_file}")
        print("   The Agent successfully controlled the file system!")
    else:
        print("❌ FAILURE: File was not created.")

if __name__ == "__main__":
    verify_agent_capabilities()
