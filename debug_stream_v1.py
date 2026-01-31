import asyncio
import os
import time
from litellm import acompletion

async def test_stream_v1():
    print("Starting stream test (V1 OpenAI Compatible)...")
    start_time = time.time()
    try:
        response = await acompletion(
            model="openai/qwen3-coder:30b",
            messages=[{"role": "user", "content": "Count from 1 to 20."}],
            api_base="http://localhost:11434/v1",
            api_key="sk-dummy",
            stream=True
        )
        
        print(f"Time to headers: {time.time() - start_time:.2f}s")
        
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
    asyncio.run(test_stream_v1())
