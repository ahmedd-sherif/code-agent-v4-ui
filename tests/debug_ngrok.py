import requests
import json
import os

NGROK_URL = "https://jo-recent-deanne.ngrok-free.dev"
MODEL = "qwen3-coder:30b"

def test_ngrok():
    print(f"Testing connectivity to: {NGROK_URL}")
    
    # 1. Test Version/Root
    try:
        resp = requests.get(f"{NGROK_URL}")
        print(f"Root GET: {resp.status_code} - {resp.text[:100]}")
    except Exception as e:
        print(f"Root GET Failed: {e}")

    # 2. Test Tags (List models)
    try:
        resp = requests.get(f"{NGROK_URL}/api/tags")
        print(f"Tags GET: {resp.status_code}")
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
            print(f"Available Models: {models}")
            if MODEL not in models and f"{MODEL}:latest" not in models:
                 print(f"WARNING: Requested model {MODEL} not found in list!")
        else:
            print(f"Error Body: {resp.text}")
    except Exception as e:
        print(f"Tags GET Failed: {e}")

    # 3. Test Generate (Chat)
    print("\nTesting Chat Completion...")
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "ping"}],
        "stream": False
    }
    
    try:
        # Ollama usually expects /api/chat
        resp = requests.post(f"{NGROK_URL}/api/chat", json=payload)
        print(f"Chat POST: {resp.status_code}")
        if resp.status_code == 200:
            print("Chat Response:", resp.json().get("message", {}).get("content"))
        else:
             print(f"Chat Failed: {resp.text}")
    except Exception as e:
        print(f"Chat Request Failed: {e}")

    # 4. Test OpenAI Compatibility /v1/chat/completions
    print("\nTesting OpenAI /v1/chat/completions...")
    openai_payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "ping v1"}],
        "stream": False
    }
    try:
        resp = requests.post(f"{NGROK_URL}/v1/chat/completions", json=openai_payload)
        print(f"OpenAI POST: {resp.status_code}")
        if resp.status_code == 200:
            print("OpenAI Response:", resp.json())
        else:
             print(f"OpenAI Failed: {resp.text}")
    except Exception as e:
        print(f"OpenAI Request Failed: {e}")

if __name__ == "__main__":
    test_ngrok()
