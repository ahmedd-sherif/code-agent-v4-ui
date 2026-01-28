from code_agent.agent import root_agent
from pydantic import BaseModel
import asyncio

class UserMessage(BaseModel):
    role: str = "user"
    content: str
    # Maybe it needs session?
    # session: str = None 

async def main():
    print("Testing run_live with local UserMessage...")
    try:
        msg = UserMessage(content="Hello")
        # run_live
        gen = root_agent.run_live(msg)
        
        async for chunk in gen:
             print(f"Chunk: {chunk}")
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
