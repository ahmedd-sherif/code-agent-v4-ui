import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path to import code_agent
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

import functools
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import json
import logging
import shutil
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import StreamingResponse
from litellm import completion

# --- Imports from Code Agent ---
from code_agent.storage import list_sessions, create_session, get_session_history, add_message, delete_session, update_session_name, get_session
from code_agent.tools import (
    write_code, edit_code, run_command, create_file, read_file, delete_file, list_directory,
    create_repository, push_code, clone_repository, git_status, git_add_all, git_commit, git_push, git_pull,
    web_search, create_project, list_projects, switch_project
)
from code_agent.agent import SYSTEM_INSTRUCTION

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# Choose between Local Ollama or Ngrok
USE_LOCAL_OLLAMA = os.getenv("USE_LOCAL_OLLAMA", "False").lower() == "true"

if USE_LOCAL_OLLAMA:
    # Local Ollama (same machine)
    os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
    os.environ["OPENAI_API_KEY"] = "sk-dummy"
    logger.info("🏠 Using Local Ollama: http://localhost:11434")
else:
    # Remote Ollama via Ngrok (different machine)
    os.environ["OPENAI_API_BASE"] = "https://jo-recent-deanne.ngrok-free.dev/v1"
    os.environ["OPENAI_API_KEY"] = "sk-dummy" 
    logger.info("🌐 Using Ngrok: https://jo-recent-deanne.ngrok-free.dev")

# --- FastAPI App ---
app = FastAPI(title="Code Agent API")

# Configure CORS for Next.js (standard port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class SessionCreate(BaseModel):
    name: str = "New Session"
    project_path: Optional[str] = None

class SessionUpdate(BaseModel):
    name: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    model: str = "openai/qwen3-coder:30b" 
    web_search: bool = False

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceRename(BaseModel):
    new_name: str

# --- Endpoints ---

@app.get("/health")
def health_check():
    """Health check endpoint to verify backend is running."""
    return {"status": "ok", "message": "Code Agent Backend is running", "service": "code-agent-api"}

@app.get("/sessions")
def get_sessions():
    """List all available chat sessions."""
    return list_sessions()

@app.post("/sessions")
def create_new_session(session: SessionCreate):
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    success = create_session(session_id, session.name, session.project_path)
    if success:
        return {"session_id": session_id, "name": session.name, "message": "Session created"}
    return {"error": "Failed to create session"}, 500

@app.delete("/sessions/{session_id}")
def delete_session_endpoint(session_id: str):
    """Delete a specific session."""
    success = delete_session(session_id)
    if success:
        return {"message": "Session deleted"}
    return {"error": "Failed to delete session"}, 500

@app.patch("/sessions/{session_id}")
def update_session(session_id: str, session: SessionUpdate):
    """Update a session's name."""
    success = update_session_name(session_id, session.name)
    if success:
        return {"message": "Session updated"}
    return {"error": "Failed to update session"}, 500

@app.get("/sessions/{session_id}/history")
def get_history(session_id: str):
    """Get chat history for a session."""
    return get_session_history(session_id)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint handling:
    1. Tool preparation (binding FS tools to project path)
    2. Message construction (System + History + User)
    3. Agent Loop (Think -> Tool Call -> Execute -> Repeat)
    4. Streaming Response with Tool Outputs
    """
    logger.info(f"Chat request for session {request.session_id} using model {request.model}")
    
    # Get session context to check if it's bound to a project
    session_info = get_session(request.session_id)
    project_path = session_info[2] if session_info else None
    
    # Prepare tools with context
    current_tools = []
    
    # If in a project, bind file system tools to that path
    if project_path and os.path.isdir(project_path):
        current_tools = [
            # Bind file tools to the specific project path
            functools.partial(write_code, base_path=project_path),
            functools.partial(edit_code, base_path=project_path),
            functools.partial(create_file, base_path=project_path),
            functools.partial(read_file, base_path=project_path),
            functools.partial(list_directory, base_path=project_path),
            # Other tools remain global or default
            run_command, # Be careful with CWD here
            web_search,
            git_status,
            git_add_all,
            git_commit,
            git_push,
            git_pull
        ]
        
        # Update function metadata so LLM sees correct names/docs after partial binding
        for t in current_tools:
            if isinstance(t, functools.partial):
                t.__name__ = t.func.__name__
                t.__doc__ = t.func.__doc__
                
    else:
        # Default global tools (operating in CWD or restricted)
        # For safety, maybe restrict file ops if not in a workspace?
        # For now, we allow them in ROOT_DIR/Created Programs
        default_workspace = ROOT_DIR / "Created Programs"
        if not default_workspace.exists(): default_workspace.mkdir()
        
        current_tools = [
            functools.partial(write_code, base_path=str(default_workspace)),
            functools.partial(edit_code, base_path=str(default_workspace)),
            functools.partial(create_file, base_path=str(default_workspace)),
            functools.partial(read_file, base_path=str(default_workspace)),
            functools.partial(list_directory, base_path=str(default_workspace)),
            run_command,
            web_search,
            create_project,
            list_projects,
            switch_project
        ]
        # Fix metadata
        for t in current_tools:
            if isinstance(t, functools.partial):
                t.__name__ = t.func.__name__
                t.__doc__ = t.func.__doc__

    tool_schemas = []
    for tool in current_tools:
        # Simple schema generation (you might want a better one)
        # This assumes tools are functions with type hints and docstrings
        import inspect
        sig = inspect.signature(tool)
        doc = inspect.getdoc(tool) or "No description"
        
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for name, param in sig.parameters.items():
            if name == "base_path": continue # Don't expose bound args
            
            param_type = "string" # Default
            if param.annotation == int: param_type = "integer"
            elif param.annotation == bool: param_type = "boolean"
            
            parameters["properties"][name] = {
                "type": param_type,
                "description": f"Parameter {name}"
            }
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(name)
                
        tool_schemas.append({
            "type": "function",
            "function": {
                "name": tool.__name__,
                "description": doc.split("\n")[0],
                "parameters": parameters
            }
        })

    async def event_generator():
        # Add system instruction
        current_system_instruction = SYSTEM_INSTRUCTION
        if project_path:
            current_system_instruction += f"\n\nYou are currently working in the project directory: {project_path}"
        
        messages = [{"role": "system", "content": current_system_instruction}]
        
        # Load history
        history = get_session_history(request.session_id)
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        # Add User Message
        messages.append({"role": "user", "content": request.message})
        add_message(request.session_id, "user", request.message)
        
        loop_count = 0
        max_loops = 15
        
        while loop_count < max_loops:
            loop_count += 1
            yield json.dumps({"type": "status", "content": f"Thinking... (Step {loop_count})"}) + "\n"
            
            try:
                response = completion(
                    model=request.model,
                    messages=messages,
                    tools=tool_schemas,
                    tool_choice="auto",
                    stream=True
                )
                
                collected_content = ""
                collected_tool_calls = []
                
                for chunk in response:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta:
                        if delta.content:
                            content_chunk = delta.content
                            collected_content += content_chunk
                            yield json.dumps({"type": "content", "content": content_chunk}) + "\n"
                        
                        if delta.tool_calls:
                            for tc in delta.tool_calls:
                                if tc.index is not None:
                                    while len(collected_tool_calls) <= tc.index:
                                        collected_tool_calls.append({"id": "", "function": {"name": "", "arguments": ""}})
                                    if tc.id: collected_tool_calls[tc.index]["id"] = tc.id
                                    if tc.function:
                                        if tc.function.name: collected_tool_calls[tc.index]["function"]["name"] += tc.function.name
                                        if tc.function.arguments: collected_tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments
                
                # Check if we have tool calls
                if collected_tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": collected_content,
                        "tool_calls": collected_tool_calls
                    })
                    add_message(request.session_id, "assistant", collected_content) # Save partial text
                    
                    for tc in collected_tool_calls:
                        tool_name = tc["function"]["name"]
                        tool_args_str = tc["function"]["arguments"]
                        tool_call_id = tc["id"]
                        
                        yield json.dumps({"type": "status", "content": f"Running Tool: {tool_name}"}) + "\n"
                        
                        # Find the tool function
                        tool_func = next((t for t in current_tools if t.__name__ == tool_name), None)
                        
                        tool_output = f"Error: Tool {tool_name} not found"
                        if tool_func:
                            try:
                                args = json.loads(tool_args_str)
                                result = tool_func(**args)
                                tool_output = str(result)
                            except Exception as e:
                                tool_output = f"Error executing {tool_name}: {str(e)}"
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_output
                        })
                        yield json.dumps({"type": "tool_output", "tool": tool_name, "output": tool_output}) + "\n"
                        
                    # Continue loop to let LLM see tool output
                    continue
                
                # If no tool calls and we have content, we are done
                if not collected_tool_calls:
                    add_message(request.session_id, "assistant", collected_content)
                    yield json.dumps({"type": "done", "content": ""}) + "\n"
                    break
                
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                yield json.dumps({"type": "error", "content": str(e)}) + "\n"
                break
                
    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/workspaces")
def list_workspaces():
    """List available workspaces (directories in 'Created Programs')."""
    workspaces_dir = ROOT_DIR / "Created Programs"
    if not workspaces_dir.exists():
        workspaces_dir.mkdir(parents=True, exist_ok=True)
        return []
    
    workspaces = []
    for item in workspaces_dir.iterdir():
        if item.is_dir():
            workspaces.append({"name": item.name, "path": str(item)})
    return workspaces

@app.post("/workspaces")
def create_workspace(workspace: WorkspaceCreate):
    """Create a new workspace directory."""
    workspaces_dir = ROOT_DIR / "Created Programs"
    if not workspaces_dir.exists(): workspaces_dir.mkdir(parents=True, exist_ok=True)
    
    path = workspaces_dir / workspace.name
    if path.exists():
        return {"error": "Workspace already exists"}, 400
    
    path.mkdir()
    return {"name": workspace.name, "path": str(path)}

@app.delete("/workspaces/{name}")
def delete_workspace(name: str):
    """Delete a workspace directory."""
    workspaces_dir = ROOT_DIR / "Created Programs"
    path = workspaces_dir / name
    if not path.exists():
        return {"error": "Workspace not found"}, 404
        
    shutil.rmtree(path)
    return {"message": "Workspace deleted"}

@app.patch("/workspaces/{name}")
def rename_workspace(name: str, ren: WorkspaceRename):
    """Rename a workspace."""
    workspaces_dir = ROOT_DIR / "Created Programs"
    old_path = workspaces_dir / name
    new_path = workspaces_dir / ren.new_name
    
    if not old_path.exists():
        return {"error": "Folder not found"}, 404
    if new_path.exists():
        return {"error": "New name already exists"}, 400
        
    old_path.rename(new_path)
    return {"message": "Renamed successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
