from code_agent.tools.project_manager import PROJECTS_BASE_DIR, create_project
import os

print(f"PROJECTS_BASE_DIR: {PROJECTS_BASE_DIR}")
print(f"Type: {type(PROJECTS_BASE_DIR)}")

# Try creating a dummy project
print("Creating test project...")
result = create_project("debug-project-123")
print(result)
