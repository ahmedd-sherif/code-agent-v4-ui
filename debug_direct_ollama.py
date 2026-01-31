import aiohttp
import asyncio
import json
import time

async def test_direct_ollama():
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "qwen3-coder:30b",
        "prompt": "Count from 1 to 20 slowly.",
        "stream": True
    }
    
    print("Starting Direct Ollama Request...")
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            print(f"Response Status: {response.status}")
            print(f"Time to headers: {time.time() - start_time:.2f}s")
            
            async for line in response.content:
                if line:
                    decoded = line.decode('utf-8').strip()
                    if decoded:
                        try:
                            json_obj = json.loads(decoded)
                            chunk = json_obj.get("response", "")
                            if chunk:
                                print(f"{time.time() - start_time:.2f}s: {chunk!r}")
                        except:
                            pass

if __name__ == "__main__":
    asyncio.run(test_direct_ollama())
