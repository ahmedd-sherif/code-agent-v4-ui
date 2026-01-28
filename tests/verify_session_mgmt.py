import requests
import uuid
import sys

BASE_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_session_mgmt():
    # 1. Create a dummy session
    name = f"Test Session {uuid.uuid4().hex[:4]}"
    res = requests.post(f"{BASE_URL}/sessions", json={"name": name})
    if res.status_code != 200:
        log("Failed to create session", "FAIL")
        return False
    
    session_id = res.json()["session_id"]
    log(f"Created session: {session_id} ({name})", "PASS")

    # 2. Rename it
    new_name = name + " UPDATED"
    res = requests.patch(f"{BASE_URL}/sessions/{session_id}", json={"name": new_name})
    if res.status_code == 200:
        log("Rename request successful", "PASS")
    else:
        log(f"Rename failed: {res.text}", "FAIL")
        return False
        
    # Verify processing
    sessions = requests.get(f"{BASE_URL}/sessions").json()
    found = next((s for s in sessions if s["session_id"] == session_id), None)
    if found and found["name"] == new_name:
        log(f"Session renamed to: {found['name']}", "PASS")
    else:
        log(f"Session rename verification failed. Found: {found}", "FAIL")

    # 3. Delete it
    res = requests.delete(f"{BASE_URL}/sessions/{session_id}")
    if res.status_code == 200:
        log("Delete request successful", "PASS")
    else:
        log(f"Delete failed: {res.text}", "FAIL")
        return False

    # Verify gone
    sessions = requests.get(f"{BASE_URL}/sessions").json()
    found = next((s for s in sessions if s["session_id"] == session_id), None)
    if not found:
        log("Session successfully removed from list", "PASS")
    else:
        log("Session still exists after delete!", "FAIL")

test_session_mgmt()
