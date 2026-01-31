import requests
import time
import json

def test_backend_latency():
    url = "http://localhost:8000/chat"
    session_id = "test-session-latency"
    
    # Create session first (if needed by logic)
    # But server.py creates session if not exists? NO, it expects session_id. 
    # Let's create one.
    requests.post("http://localhost:8000/sessions", json={"name": "Latency Test"})
    
    payload = {
        "session_id": session_id,
        "message": "Count from 1 to 5.",
        "model": "openai/qwen3-coder:30b" # Matching server default
    }
    
    # We need to ensure session exists in DB if logic enforces it
    # server.py line 140: session_info = get_session(request.session_id)
    # If None, it proceeds with project_path=None. It doesn't crash?
    # db.py get_session returns None. 
    # server.py: project_path = session_info["project_path"] if session_info else None
    # So it handles missing session gracefully for project_path lookup.
    # But does it need to exist for add_message? 
    # Line 248: add_message(..., "user", ...) -> checks foreign key?
    # db.py: FOREIGN KEY (session_id) REFERENCES sessions (session_id)
    # SQLite *usually* enforces FK only if PRAGMA foreign_keys = ON. 
    # Let's create the session properly to be safe.
    
    requests.post("http://localhost:8000/sessions", json={"name": "Latency Test", "session_id": session_id})
    # Wait, create_session endpoint generates uuid. I cannot force session_id easily via API unless I modify it?
    # Line 99: create_new_session(session: SessionCreate) -> session_id = uuid.uuid4()
    # So I must capture the ID from response.
    
    print("Creating session...")
    resp = requests.post("http://localhost:8000/sessions", json={"name": "Latency Test"})
    if resp.status_code != 200:
        print(f"Failed to create session: {resp.text}")
        return
        
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")
    payload["session_id"] = session_id
    
    print(f"Sending request to {url}...")
    start_time = time.time()
    
    try:
        with requests.post(url, json=payload, stream=True) as response:
            print(f"Time to headers: {time.time() - start_time:.4f}s")
            
            first_byte_time = None
            
            for line in response.iter_lines():
                if line:
                    if first_byte_time is None:
                        first_byte_time = time.time()
                        print(f"Time to first chunk: {first_byte_time - start_time:.4f}s")
                    
                    # Decoded check
                    # print(line) 
            
            total_time = time.time() - start_time
            print(f"Total time: {total_time:.4f}s")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend_latency()
