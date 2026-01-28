"""
Llama 405B - Using provider that supports tools
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from code_agent.tools.code_writer import write_code, edit_code
from code_agent.tools.terminal import run_command
from code_agent.tools.file_manager import create_file, read_file, list_directory
from code_agent.tools.project_manager import create_project, list_projects, switch_project

SYSTEM_INSTRUCTION = """You are an AI coding assistant.

## Steps:
1. create_project(name, description)
2. write_code(filename, code, description)
3. Done!

Be concise.
"""

# Using Mistral Small which supports tool use
root_agent = Agent(
    name="llama_405b",
    model=LiteLlm(model="openrouter/mistralai/mistral-small-3.1-24b-instruct:free"),
    description="Mistral Small 24B - Fast with Tools",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        create_project, list_projects, switch_project,
        write_code, edit_code, run_command,
        create_file, read_file, list_directory,
    ],
)
