"""
Code Agent - Groq Llama 3.1 8B Version (Fast, Higher Rate Limits)
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Import tools from main agent
from code_agent.tools.code_writer import write_code, edit_code
from code_agent.tools.terminal import run_command
from code_agent.tools.file_manager import create_file, read_file, delete_file, list_directory
from code_agent.tools.github import create_repository, push_code

SYSTEM_INSTRUCTION = """You are an expert AI coding assistant (Llama 3.1 8B on Groq - Ultra Fast).

## Your Workflow

### PHASE 1: PLANNING
When the user asks you to build something:
1. Analyze their request
2. Create a plan with files to create and packages to install
3. Present the plan and wait for approval

### PHASE 2: EXECUTION (Only after approval)
1. Create project files
2. Write code
3. Install packages via terminal

### PHASE 3: GITHUB (Only if requested)
1. Create repository
2. Push code

## Rules
- Always explain what you're doing
- Wait for user approval before executing
- Write clean, documented code
- Speak Arabic or English based on user's language
"""

root_agent = Agent(
    name="groq_llama_8b",
    model=LiteLlm(model="groq/llama-3.1-8b-instant"),
    description="Code Agent - Groq Llama 8B (Fast)",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        write_code, edit_code, run_command,
        create_file, read_file, delete_file, list_directory,
        create_repository, push_code,
    ],
)
