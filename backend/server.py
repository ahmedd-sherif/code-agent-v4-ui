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
# Use OpenAI compatible endpoint via Ngrok
os.environ["OPENAI_API_BASE"] = "https://jo-recent-deanne.ngrok-free.dev/v1"
os.environ["OPENAI_API_KEY"] = "sk-dummy" # Required by Client, ignored by Ollama

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
def update_session_endpoint(session_id: str, update: SessionUpdate):
    """Update session name."""
    success = update_session_name(session_id, update.name)
    if success:
        return {"message": "Session updated"}
    return {"error": "Failed to update session"}, 500

@app.get("/sessions/{session_id}/history")
def get_history(session_id: str):
    """Get history for a specific session."""
    return get_session_history(session_id)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Streaming chat endpoint with agent loop."""
    
    # Get previous history
    history = get_session_history(request.session_id, limit=20)
    
    # Get session details for workspace context
    session = get_session(request.session_id)
    project_path = session.get("project_path") if session else None
    
    # Save user message
    add_message(request.session_id, "user", request.message)
    
    # Helper to bind tools to workspace
    def bind_tool_to_path(tool, path):
        @functools.wraps(tool)
        def wrapper(*args, **kwargs):
            kwargs['base_path'] = path
            return tool(*args, **kwargs)
        return wrapper

    # Helper to convert python function to OpenAI tool schema
    def function_to_schema(func):
        import inspect
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""
        
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for name, param in sig.parameters.items():
            if name == "self" or name == "cls": continue
            
            param_type = "string"
            if param.annotation == int: param_type = "integer"
            elif param.annotation == bool: param_type = "boolean"
            elif param.annotation == list: param_type = "array"
            elif param.annotation == dict: param_type = "object"
            
            parameters["properties"][name] = {"type": param_type, "description": name}
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(name)
                
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc.split("\n")[0],
                "parameters": parameters
            }
        }

    async def event_generator():
        # Prepare tools
        # Core tools that might use filesystem
        fs_tools = [
            write_code, edit_code, create_file, read_file, delete_file, list_directory
        ]
        
        # Other tools
        other_tools = [
             run_command,
             create_repository, push_code, clone_repository, git_status, git_add_all, git_commit, git_push, git_pull,
             create_project, list_projects, switch_project
        ]
        
        current_tools = []
        
        # Bind filesystem tools if project_path is set
        if project_path:
            for t in fs_tools:
                current_tools.append(bind_tool_to_path(t, project_path))
        else:
            current_tools.extend(fs_tools)
            
        current_tools.extend(other_tools)
            
        if request.web_search:
            current_tools.append(web_search)
            
        # Convert to OpenAI Schemas
        tool_schemas = [function_to_schema(t) for t in current_tools]
            
        # Prepare system instruction
        current_system_instruction = SYSTEM_INSTRUCTION
        if project_path:
             current_system_instruction += f"\n\nCURRENT WORKING DIRECTORY: {project_path}. All file operations are restricted to this directory."
             
        if request.web_search:
            current_system_instruction += "\n\nIMPORTANT: Web Search is ENABLED. You MUST use the `web_search` tool if you need external information."
            
        messages = [{"role": "system", "content": current_system_instruction}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": request.message})
        
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
                                        if tc.function.name: collected_tool_calls[tc.index]["function"]["name"] = tc.function.name
                                        if tc.function.arguments: collected_tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments

                # Process Tool Calls
                if collected_tool_calls:
                    # Notify UI that tools are executing
                    yield json.dumps({"type": "status", "content": f"Executing {len(collected_tool_calls)} tools..."}) + "\n"
                    
                    # Add assistant's tool_calls to history
                    messages.append({
                        "role": "assistant",
                        "content": collected_content,
                        "tool_calls": collected_tool_calls
                    })
                    add_message(request.session_id, "assistant", collected_content) # Note: we might want to store tool calls too in DB in future

                    # Execute each tool
                    for tc in collected_tool_calls:
                        func_name = tc["function"]["name"]
                        func_args_str = tc["function"]["arguments"]
                        call_id = tc["id"]
                        
                        try:
                            func_args = json.loads(func_args_str)
                            
                            # Find matching tool function
                            tool_func = next((t for t in current_tools if t.__name__ == func_name or getattr(t, "__name__", "") == func_name), None)
                            
                            if tool_func:
                                # Notify UI of specific action
                                yield json.dumps({"type": "status", "content": f"Running: {func_name}..."}) + "\n"
                                
                                # Execute
                                tool_result = tool_func(**func_args)
                                tool_output = json.dumps(tool_result)
                            else:
                                tool_output = f"Error: Tool '{func_name}' not found."
                                
                        except Exception as e:
                            tool_output = f"Error executing tool '{func_name}': {str(e)}"
                        
                        # Yield output to UI
                        yield json.dumps({"type": "tool_output", "content": f"Op: {func_name}\nResult: {tool_output}"}) + "\n"
                        
                        # Add tool result to history for next loop iteration
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "name": func_name,
                            "content": tool_output
                        })
                    
                    # Loop continues to next iteration (LLM sees tool outputs)
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
    workspaces_dir.mkdir(parents=True, exist_ok=True)
    
    target_path = workspaces_dir / workspace.name
    if target_path.exists():
         return {"error": "Workspace already exists"}, 400
    
    try:
        target_path.mkdir()
        return {"message": "Workspace created", "path": str(target_path)}
    except Exception as e:
        return {"error": str(e)}, 500

@app.delete("/workspaces/{name}")
def delete_workspace(name: str):
    """Delete a workspace directory."""
    workspaces_dir = ROOT_DIR / "Created Programs"
    target_path = workspaces_dir / name
    
    if not target_path.exists():
        return {"error": "Workspace not found"}, 404
        
    try:
        shutil.rmtree(target_path)
        return {"message": "Workspace deleted"}
    except Exception as e:
        return {"error": str(e)}, 500

@app.patch("/workspaces/{name}")
def rename_workspace(name: str, update: WorkspaceRename):
    """Rename a workspace directory."""
    workspaces_dir = ROOT_DIR / "Created Programs"
    old_path = workspaces_dir / name
    new_path = workspaces_dir / update.new_name
    
    if not old_path.exists():
        return {"error": "Workspace not found"}, 404
    if new_path.exists():
        return {"error": "Destination name already exists"}, 400
        
    try:
        old_path.rename(new_path)
        return {"message": "Workspace renamed"}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    # Run the server on port 8000
    print("🚀 Starting Code Agent Backend on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
