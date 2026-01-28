from code_agent.agent import root_agent
import inspect

print("Methods of root_agent:")
for name in dir(root_agent):
    if not name.startswith("_"):
        print(name)
