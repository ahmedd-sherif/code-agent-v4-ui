"""
Llama 70B - Using Nous Hermes which supports tools
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

# Using Nous Hermes 405B which might support tools
root_agent = Agent(
    name="llama_70b",
    model=LiteLlm(model="openrouter/nousresearch/hermes-3-llama-3.1-405b:free"),
    description="Hermes 3 405B - Powerful",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        create_project, list_projects, switch_project,
        write_code, edit_code, run_command,
        create_file, read_file, list_directory,
    ],
)
