"""
Code Agent - OpenRouter Qwen3 Coder
Best free model for coding!
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from code_agent.tools.code_writer import write_code, edit_code
from code_agent.tools.terminal import run_command
from code_agent.tools.file_manager import create_file, read_file, delete_file, list_directory
from code_agent.tools.github import create_repository, push_code
from code_agent.tools.project_manager import (
    create_project, list_projects, switch_project,
    get_current_project, save_progress, get_project_history
)

SYSTEM_INSTRUCTION = """You are an expert AI coding assistant.

## IMPORTANT: Use tools to create files!
1. create_project(name, description) - FIRST!
2. write_code(filename, code, description) - For each file

## Rules:
- Always create_project() before writing code
- Always use write_code() tool, don't just show code
- Speak Arabic or English based on user
"""

root_agent = Agent(
    name="qwen3_coder",
    model=LiteLlm(model="openrouter/qwen/qwen3-coder:free"),
    description="Code Agent - Qwen3 Coder (Best for coding)",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        create_project, list_projects, switch_project,
        get_current_project, save_progress, get_project_history,
        write_code, edit_code, run_command,
        create_file, read_file, delete_file, list_directory,
        create_repository, push_code,
    ],
)
