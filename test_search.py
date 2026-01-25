from code_agent.tools.web_search import web_search
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Web Search Tool...")
api_key = os.getenv("TAVILY_API_KEY")
print(f"API Key present: {bool(api_key)}")

# Simple search
print("\n--- Searching for 'python latest version' ---")
result = web_search("what is the latest python version released in 2024 or 2025?")
print(result)

# Documentation search test
print("\n--- Searching for 'fastapi documentation hello world' ---")
result = web_search("fastapi hello world example code")
print(result)

if "Error" not in result:
    print("\nSUCCESS: Web search works!")
else:
    print("\nFAILURE: Search returned error.")
