import asyncio
import os
import time
from litellm import acompletion

# Setup Env for Native Ollama
if "OPENAI_API_BASE" in os.environ: del os.environ["OPENAI_API_BASE"]
os.environ["OPENAI_API_KEY"] = "sk-dummy"

async def test_stream():
    print("Starting stream test...")
    start_time = time.time()
    try:
        response = await acompletion(
            model="ollama/qwen3-coder:30b",
            messages=[{"role": "user", "content": "Count from 1 to 10."}],
            api_base="http://localhost:11434",
            stream=True
        )
        
        print(f"Time to first chunk: {time.time() - start_time:.2f}s")
        
        chunk_count = 0
        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                print(f"{time.time() - start_time:.2f}s: {delta!r}")
                chunk_count += 1
                
        print(f"\nTotal chunks: {chunk_count}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stream())
