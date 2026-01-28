import requests
import json
import time

def verify_autonomy():
    print("🔍 Testing Autonomous Agent Loop...")
    
    # Create a dummy session
    session_res = requests.post("http://localhost:8000/sessions", json={"name": "AutonomyTest"})
    if session_res.status_code != 200:
        print("❌ Failed to create session")
        return
    
    session_id = session_res.json()["session_id"]
    print(f"✅ Session created: {session_id}")
    
    # Send a request that SHOULD trigger a tool
    # We ask for a file creation. The new loop should execute it.
    payload = {
        "session_id": session_id,
        "message": "Create a file named autonomy_check.txt with content 'loop works'",
        "model": "openai/qwen3-coder:30b",
        "web_search": False
    }
    
    print("🤖 Sending Chat Request...")
    try:
        with requests.post("http://localhost:8000/chat", json=payload, stream=True) as r:
            tool_executed = False
            for line in r.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if data.get("type") == "status":
                            print(f"   [Status] {data['content']}")
                            if "Executing" in data['content']:
                                tool_executed = True
                        if data.get("type") == "tool_output":
                            print(f"   [Tool Output] {data['content']}")
                    except:
                        pass
            
            if tool_executed:
                print("✅ SUCCESS: The backend executed the tools autonomously!")
            else:
                print("❌ FAILURE: No tool execution status observed.")
                
    except Exception as e:
        print(f"❌ Error during request: {e}")

if __name__ == "__main__":
    verify_autonomy()
