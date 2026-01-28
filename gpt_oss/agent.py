"""
OpenAI GPT-OSS 120B - Free OpenAI model with tool support
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

root_agent = Agent(
    name="gpt_oss",
    model=LiteLlm(model="openrouter/openai/gpt-oss-120b:free"),
    description="OpenAI GPT-OSS 120B - Free OpenAI",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        create_project, list_projects, switch_project,
        write_code, edit_code, run_command,
        create_file, read_file, list_directory,
    ],
)
