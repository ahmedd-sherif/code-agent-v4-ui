import requests
import time
from pathlib import Path
import json

BASE_URL = "http://localhost:8000"
ROOT_DIR = Path("d:/Ahmed Sherif/Digilians/Projects/Code Agent")
CREATED_PROGRAMS = ROOT_DIR / "Created Programs"

def verify_isolation():
    print("Verifying Workspace Isolation...")
    
    ws_name = "IsoTest"
    session_name = "IsoSession"
    filename = "isolated.txt"
    
    # 1. Create Workspace
    print(f"Creating workspace '{ws_name}'...")
    requests.post(f"{BASE_URL}/workspaces", json={"name": ws_name})
    
    ws_path = CREATED_PROGRAMS / ws_name
    if not ws_path.exists():
        print("FAILED: Workspace folder not created.")
        return

    # 2. Create Session LINKED to Workspace
    print(f"Creating session '{session_name}' linked to '{ws_path}'...")
    res = requests.post(f"{BASE_URL}/sessions", json={
        "name": session_name,
        "project_path": str(ws_path)
    })
    if res.status_code != 200:
        print(f"FAILED to create session: {res.text}")
        return
    session_id = res.json()["session_id"]
    print(f"Session ID: {session_id}")

    # 3. Chat: Create File
    print(f"Asking agent to create '{filename}'...")
    # We use a direct tool call if possible, or just ask safely.
    # To be robust, let's just ask. The agent should use `create_file` or `write_code`.
    # Both are bound to the path.
    msg = f"Create a file named {filename} with content 'Hello Isolation'"
    
    # We need to stream reading or just wait?
    # The chat endpoint streams. We can just read the response.
    res = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": msg,
        "model": "openai/qwen3-coder:30b"
    }, stream=True)
    
    content = ""
    for line in res.iter_lines():
        if line:
            try:
                data = json.loads(line)
                if data["type"] == "content":
                    content += data["content"]
            except:
                pass
    
    print("Agent reply received.")
    
    # 4. Verify File Location
    expected_file = ws_path / filename
    unexpected_file = ROOT_DIR / filename
    
    if expected_file.exists():
        print(f"SUCCESS: File created in workspace: {expected_file}")
    else:
        print(f"FAILED: File NOT found in workspace: {expected_file}")
        
    if unexpected_file.exists():
        print(f"FAILED: File created in ROOT! Isolation failed: {unexpected_file}")
        # Cleanup
        unexpected_file.unlink()
    else:
        print("SUCCESS: File NOT created in root.")

    # Cleanup
    # requests.delete(f"{BASE_URL}/workspaces/{ws_name}") # Optional cleanup

if __name__ == "__main__":
    verify_isolation()
