"""
Code Agent - Simple and focused
Using Mistral Devstral for stability
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools.code_writer import write_code, edit_code
from .tools.terminal import run_command
from .tools.file_manager import create_file, read_file, list_directory
from .tools.web_search import web_search
from .tools.git_tools import clone_repository, git_status, git_add_all, git_commit, git_push, git_pull
from .tools.project_manager import create_project, list_projects, switch_project
from .storage import create_session, add_message, get_session_history, list_sessions

SYSTEM_INSTRUCTION = """You are an AI coding assistant. Be simple and direct.

## capabilities:
- Write and edit code
- Manage projects and files
- Run terminal commands
- **Search the web** for documentation or solutions
- **Git Operations**: Clone, Status, Commit, Push
- **Persistent Memory**: Manage sessions and history

## When starting a conversation:
1. `list_sessions()` to see if there's history.
2. `get_session_history(session_id)` to recall context if needed.

## When user asks a question, or if you don't know something:
1. YOU MUST use `web_search(query)` to find information.
2. DO NOT say you cannot search the internet. You have the tool. USE IT.
3. Synthesize the answer from the search results.

## When user asks to clone or work on a repo:
1. Use `clone_repository(url, target_path)`.
2. Navigate user request.
3. Use `git_add_all`, `git_commit`, `git_push` when asked to save/upload.

## Example:
User: "make a calculator"
1. create_project("calculator", "Simple calc")
2. write_code("calc.py", "print(1+1)", "Calculator code")  
3. Reply: "Done! Created calculator project."

## Rules:
- Do NOT call get_current_project or save_progress
- Create complete code in ONE call per file
- Be brief
"""

root_agent = Agent(
    name="code_agent",
    model=LiteLlm(model="openrouter/mistralai/devstral-2512:free"),
    description="Simple Code Agent",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        create_project,
        list_projects,
        switch_project,
        write_code,
        edit_code,
        run_command,
        create_file,
        read_file,
        list_directory,
        web_search,
        clone_repository,
        git_status,
        git_add_all,
        git_commit,
        git_push,
        git_pull,
        create_session,
        add_message,
        get_session_history,
        list_sessions,
    ],
)

__all__ = ["root_agent"]
