from code_agent.agent import root_agent
import sys

print("Testing agent invocation...")
try:
    # Attempt 1: query
    response = root_agent.query("Hello, are you ready?")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    if hasattr(response, 'text'):
        print(f"Response text: {response.text}")
except Exception as e:
    print(f"Error calling agent: {e}")
    # Inspect agent methods
    print("Agent dir:", dir(root_agent))
