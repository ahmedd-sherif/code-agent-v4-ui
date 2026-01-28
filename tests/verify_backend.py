import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_health():
    try:
        res = requests.get(f"{BASE_URL}/health")
        if res.status_code == 200:
            log("Health check passed: " + str(res.json()), "PASS")
            return True
        else:
            log(f"Health check failed: {res.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"Backend not reachable: {e}", "FAIL")
        return False

def test_session_flow():
    # 1. List Sessions (Initial)
    res = requests.get(f"{BASE_URL}/sessions")
    initial_count = len(res.json())
    log(f"Initial sessions count: {initial_count}")
    
    # 2. Create Session
    payload = {"name": "Test Session Verify", "project_path": None}
    res = requests.post(f"{BASE_URL}/sessions", json=payload)
    if res.status_code == 200 and "session_id" in res.json():
        session_id = res.json()["session_id"]
        log(f"Created session: {session_id}", "PASS")
    else:
        log(f"Failed to create session: {res.text}", "FAIL")
        return False
        
    # 3. Verify Added
    res = requests.get(f"{BASE_URL}/sessions")
    new_count = len(res.json())
    if new_count == initial_count + 1:
        log("Session list updated correctly", "PASS")
    else:
        log(f"Session list count mismatch (Expected {initial_count+1}, got {new_count})", "FAIL")

    # 4. Test Chat (Simple)
    log("Testing Chat Stream...")
    chat_payload = {
        "session_id": session_id,
        "message": "Hello, simply reply with 'PONG'",
        "model": "gemini-1.5-flash",
        "web_search": False
    }
    
    try:
        with requests.post(f"{BASE_URL}/chat", json=chat_payload, stream=True) as r:
            if r.status_code == 200:
                collected_content = ""
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        if data["type"] == "content":
                            collected_content += data["content"]
                
                log(f"Received chat response: {collected_content[:50]}...", "PASS")
            else:
                log(f"Chat endpoint failed: {r.status_code}", "FAIL")
    except Exception as e:
        log(f"Chat test error: {e}", "FAIL")

    return True

if __name__ == "__main__":
    if test_health():
        test_session_flow()
