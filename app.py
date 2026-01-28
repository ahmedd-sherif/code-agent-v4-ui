import streamlit as st
import uuid
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
from code_agent.storage import init_db, list_sessions, create_session, get_session_history, add_message
from code_agent.agent import SYSTEM_INSTRUCTION
# Import tools directly
from code_agent.tools import (
    write_code, edit_code, run_command, create_file, read_file, delete_file, list_directory,
    create_repository, push_code, clone_repository, git_status, git_add_all, git_commit, git_push, git_pull,
    web_search, create_project, list_projects, switch_project, get_current_project, save_progress, get_project_history,
    create_session as tool_create_session, add_message as tool_add_message, get_session_history as tool_get_history, list_sessions as tool_list_sessions
)
import litellm
from litellm import completion

# --- Dialogs ---
@st.dialog("Start New Conversation")
def open_new_session_dialog():
    new_session_name = st.text_input("Chat Name", placeholder="e.g. Debugging login")
    
    # Project selection
    existing_projects = list(set([s["project_path"] for s in list_sessions() if s.get("project_path")]))
    existing_projects.insert(0, "Playground (No Workspace)")
    existing_projects.append("➕ New Workspace...")
    
    target_project = st.selectbox("Workspace", existing_projects)
    
    final_project_path = None
    new_proj_name = None
    
    if target_project == "➕ New Workspace...":
        base_dir = "D:\\Ahmed Sherif\\Digilians\\Projects\\Code Agent\\Created Programs"
        new_proj_name = st.text_input("Folder Name", placeholder="my-new-app")
    elif target_project != "Playground (No Workspace)":
        final_project_path = target_project
    
    if st.button("Create Session", type="primary", use_container_width=True):
        if target_project == "➕ New Workspace..." and new_proj_name:
             final_project_path = f"{base_dir}\\{new_proj_name}"
        
        sid = str(uuid.uuid4())
        create_session(sid, new_session_name or "New Session", project_path=final_project_path)
        st.session_state.current_session_id = sid
        st.rerun()



# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page Config
# Updated Project Path Configuration
st.set_page_config(
    page_title="Code Agent V4",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
init_db()

# --- Tools Definition for LiteLLM ---
# We need to format function schemas for LiteLLM.
# Since we have the functions, we can try using litellm's auto-schema or define them.
# The previous agent.py passed functions directly. LiteLLM supports that.

available_tools = [
     write_code, edit_code, run_command, create_file, read_file, delete_file, list_directory,
     create_repository, push_code, clone_repository, git_status, git_add_all, git_commit, git_push, git_pull,
     web_search, create_project, list_projects, switch_project, get_current_project, save_progress, get_project_history,
     tool_create_session, tool_add_message, tool_get_history, tool_list_sessions
]

# Map for execution
tool_map = {t.__name__: t for t in available_tools}

# --- Context Initialization (Must be before sidebar) ---
if "current_session_id" not in st.session_state:
    existing_sessions = list_sessions()
    if existing_sessions:
        st.session_state.current_session_id = existing_sessions[0]["session_id"]
    else:
        st.session_state.current_session_id = str(uuid.uuid4())
        create_session(st.session_state.current_session_id, "New Session")

current_id = st.session_state.current_session_id

# Find current session data to get path
all_sessions = list_sessions()
current_session_data = next((s for s in all_sessions if s["session_id"] == current_id), None)
current_project_path = None

if current_session_data and current_session_data.get("project_path"):
    current_project_path = current_session_data["project_path"]
    try:
        switch_project(current_project_path)
    except Exception as e:
        logger.error(f"Could not switch path: {e}")


# --- Sidebar ---
with st.sidebar:
    # 1. Start Conversation (Global)
    if st.button("➕ Start conversation", use_container_width=True, type="primary"):
        open_new_session_dialog()
    
    st.write("") # Spacer

    # 2. Workspaces Section
    st.markdown("### Workspaces")
    
    sessions = list_sessions()
    
    # Group sessions
    from collections import defaultdict
    workspace_sessions = defaultdict(list)
    playground_sessions = []
    
    for s in sessions:
        path = s.get("project_path")
        if path:
            folder_name = path.replace("\\", "/").split("/")[-1]
            workspace_sessions[(folder_name, path)].append(s)
        else:
            playground_sessions.append(s)
            
    # Render Workspaces
    for (folder_name, path), proj_sessions in workspace_sessions.items():
        # Use expander for each workspace
        # Check if active is in this workspace
        is_active_ws = current_project_path == path
        
        with st.expander(f"📂 {folder_name}", expanded=is_active_ws):
            # Show sessions
            for sess in proj_sessions:
                label = sess.get("name", "Untitled") or "Untitled"
                if len(label) > 18: label = label[:16] + "..."
                
                is_active = sess["session_id"] == current_id
                prefix = "🔵" if is_active else "▪️"
                
                # Use a button that looks like a list item
                if st.button(f"{prefix} {label}", key=sess["session_id"], use_container_width=True):
                    st.session_state.current_session_id = sess["session_id"]
                    st.rerun()

    # Open Workspace Button (Simulated)
    if st.button("➕ Open Workspace", use_container_width=True):
        st.session_state.show_new_session_form = True # Re-use form for now, user can pick "New Workspace"
    
    st.write("")
    
    # 3. Playground Section
    with st.expander("🛝 Playground", expanded=True):
         for sess in playground_sessions:
            label = sess.get("name", "Untitled") or "Untitled"
            if len(label) > 18: label = label[:16] + "..."
            
            is_active = sess["session_id"] == current_id
            prefix = "🔵" if is_active else "▪️"
                
            if st.button(f"{prefix} {label}", key=sess["session_id"], use_container_width=True):
                st.session_state.current_session_id = sess["session_id"]
                st.rerun()
                
    st.divider()

    # 4. File Explorer (Context Aware)
    if current_project_path:
        st.markdown(f"**Files: {current_project_path.split(os.sep)[-1]}**")
        try:
            import os
            # Simple recursive walker or just top level
            for root, dirs, files in os.walk(current_project_path):
                level = root.replace(current_project_path, '').count(os.sep)
                indent = '&nbsp;' * 3 * level
                base_name = os.path.basename(root)
                if base_name == ".git" or base_name == "__pycache__" or base_name == ".venv": 
                    continue
                if level == 0:
                     pass # Root is header
                else:
                     st.markdown(f"{indent}� {base_name}", unsafe_allow_html=True)
                
                subindent = '&nbsp;' * 3 * (level + 1)
                for f in files:
                    st.markdown(f"{subindent}📄 {f}", unsafe_allow_html=True)
                
                if level > 2: break # Limit depth
        except Exception as e:
             st.caption("Error reading files")
    
    st.divider()
    
    # 5. Settings
    with st.expander("⚙️ Settings"):
        if "ollama_url" not in st.session_state:
            st.session_state.ollama_url = "https://jo-recent-deanne.ngrok-free.dev"
            
        new_url = st.text_input("Ollama API URL", value=st.session_state.ollama_url)
        if new_url != st.session_state.ollama_url:
            st.session_state.ollama_url = new_url
            st.rerun()

# --- Main Interface ---
st.title("🤖 Code Agent Workspace")

# --- Top Toolbar (Model & Tools) ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    # Model Selection
    # Local Qwen3-Coder via Ollama
    # Default to localhost, can be overridden via Settings
    # Model Selection
    # Local Qwen3-Coder via Ollama
    # Default to localhost, can be overridden via Settings
    if "ollama_url" not in st.session_state:
        st.session_state.ollama_url = "https://jo-recent-deanne.ngrok-free.dev"
        
    LOCAL_OLLAMA_URL = st.session_state.ollama_url
    
    model_options = {
        "🏠 Qwen3-Coder (Local - No Limits!)": "ollama/qwen3-coder:30b",
        "Gemini 2.0 Flash (Google)": "gemini/gemini-2.0-flash-exp",
        "Qwen3-Coder (OpenRouter)": "openrouter/qwen/qwen3-coder:free",
        "GPT-OSS-120B (OpenRouter)": "openrouter/openai/gpt-oss-120b:free",
        "Llama 3.1 405B (OpenRouter)": "openrouter/meta-llama/llama-3.1-405b-instruct:free",
        "DeepSeek R1 (OpenRouter)": "openrouter/deepseek/deepseek-r1:free",
    }
    selected_model_label = st.selectbox("🧠 Model", list(model_options.keys()), index=0, label_visibility="collapsed")
    selected_model = model_options[selected_model_label]
    
    # Set Ollama base URL for local model
    if "Local" in selected_model_label:
        import os
        os.environ["OLLAMA_API_BASE"] = LOCAL_OLLAMA_URL

with col2:
    # Web Search Toggle (Moved here)
    use_web_search = st.toggle("🌐 Web Search", value=True)

with col3:
    st.write("") # Spacer

st.divider()

# --- Sticky Header CSS ---
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stColumn"]) {
        position: sticky;
        top: 2.875rem;
        background-color: #0e1117; 
        z-index: 999;
        padding-top: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #303030;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Top Toolbar (Model & Tools) ---
# ... (Toolbar code remains here effectively due to the CSS selector targeting columns) ...

# ... (Main Interface code continues) ...

# --- Context Status Display ---
if current_project_path:
    st.caption(f"📍 Active Workspace: `{current_project_path}`")
else:
    st.caption("📍 Global Context (No Workspace)")

# Load History
history = get_session_history(current_id)

# Display Messages
for msg in history:
    with st.chat_message(msg["role"], avatar="⚙️" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("What would you like to build?"):
    # 1. User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    add_message(current_id, "user", prompt)
    
    # Reload history
    history = get_session_history(current_id)

    # 2. Agent Loop
    if prompt: # Only run if there is input
        # User requested "Circle that keeps loading" -> standard st.spinner or simpler icon
        with st.chat_message("assistant", avatar="⚙️"): 
            # Container for the 'thinking' process
            with st.status("Thinking...", expanded=True) as status:
                message_placeholder = st.empty()
                full_response = ""
                
                # Filter tools based on toggle
                current_tools = [t for t in available_tools if t != web_search] # Remove search first
                if use_web_search:
                    current_tools.append(web_search) # Add back if enabled
                
                # Construct messages for LLM
                # System instruction first
                current_system_instruction = SYSTEM_INSTRUCTION
                # Inject Context Awareness
                if current_project_path:
                     current_system_instruction += f"\n\nCURRENT WORKING DIRECTORY: {current_project_path}\nAlways create files relative to this path."
        
                if use_web_search:
                     current_system_instruction += "\n\nIMPORTANT: Web Search is ENABLED. You MUST use the `web_search` tool if you need external information."
                
                # Robustness: Force Tool Usage instruction for weaker models
                if "llama" in selected_model or "mistral" in selected_model:
                    current_system_instruction += "\n\nCRITICAL: DO NOT write code to call tools. YOU MUST use the provided function tools directly. Do not output text like 'write_code(...)', actually call the function."

                messages = [{"role": "system", "content": current_system_instruction}]
                # Append history
                for h in history:
                    messages.append({"role": h["role"], "content": h["content"]})
                    
                try:
                    loop_count = 0
                    max_loops = 15  # Increased slightly
                    consecutive_same_tool = 0
                    last_tool_name = None
                    write_code_count = 0
                    
                    while loop_count < max_loops:
                        loop_count += 1
                        status.update(label=f"Thinking... (Step {loop_count})", state="running")
                        
                        # If too many write_code calls, inject a message asking to wrap up
                        if write_code_count >= 5 and not any("Please summarize" in str(m.get("content", "")) for m in messages if isinstance(m, dict)):
                            messages.append({
                                "role": "user", 
                                "content": "Great work! Please summarize what you created and stop creating more files."
                            })
                        
                        try:
                            # Use streaming for real-time response
                            response = completion(
                                model=selected_model, 
                                messages=messages,
                                tools=current_tools,
                                tool_choice="auto",
                                stream=True,  # Enable streaming!
                                extra_headers={
                                    "ngrok-skip-browser-warning": "true",
                                    "User-Agent": "CodeAgent/1.0"
                                }
                            )
                            
                            # Collect streamed response
                            collected_content = ""
                            collected_tool_calls = []
                            current_tool_call = None
                            
                            for chunk in response:
                                delta = chunk.choices[0].delta if chunk.choices else None
                                if delta:
                                    # Handle content streaming
                                    if delta.content:
                                        collected_content += delta.content
                                        # Show streaming text in real-time!
                                        message_placeholder.markdown(collected_content + "▌")
                                    
                                    # Handle tool calls
                                    if delta.tool_calls:
                                        for tc in delta.tool_calls:
                                            if tc.index is not None:
                                                # New tool call or continuing existing one
                                                while len(collected_tool_calls) <= tc.index:
                                                    collected_tool_calls.append({"id": "", "function": {"name": "", "arguments": ""}})
                                                
                                                if tc.id:
                                                    collected_tool_calls[tc.index]["id"] = tc.id
                                                if tc.function:
                                                    if tc.function.name:
                                                        collected_tool_calls[tc.index]["function"]["name"] = tc.function.name
                                                    if tc.function.arguments:
                                                        collected_tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments
                            
                            # Build final message object
                            class StreamedMessage:
                                def __init__(self, content, tool_calls):
                                    self.role = "assistant"
                                    self.content = content
                                    self.tool_calls = tool_calls
                                    
                                def to_dict(self):
                                    return {
                                        "role": self.role,
                                        "content": self.content,
                                        "tool_calls": [
                                            {
                                                "id": tc.id,
                                                "type": "function",
                                                "function": {
                                                    "name": tc.function.name,
                                                    "arguments": tc.function.arguments
                                                }
                                            } for tc in (self.tool_calls or [])
                                        ]
                                    }
                            
                            class StreamedToolCall:
                                def __init__(self, data):
                                    self.id = data["id"]
                                    self.type = "function"
                                    self.function = type('obj', (object,), {
                                        'name': data["function"]["name"],
                                        'arguments': data["function"]["arguments"]
                                    })()
                            
                            final_tool_calls = [StreamedToolCall(tc) for tc in collected_tool_calls if tc["function"]["name"]] if collected_tool_calls else None
                            msg = StreamedMessage(collected_content, final_tool_calls)
                            
                        except Exception as api_error:
                            # Handle API errors gracefully
                            error_msg = str(api_error)
                            if "empty" in error_msg.lower():
                                full_response = f"✅ Done! Created {write_code_count} file(s). Check your workspace folder."
                                message_placeholder.markdown(full_response)
                                add_message(current_id, "assistant", full_response)
                                status.update(label="Complete!", state="complete", expanded=False)
                                break
                            else:
                                # Parse error message if it's JSON
                                try:
                                    import json
                                    # LiteLLM sometimes returns JSON in string
                                    err_json = json.loads(error_msg.replace("'", '"')) # Basic cleanup
                                    if "message" in err_json:
                                        st.error(f"❌ Error: {err_json['message']}")
                                    else:
                                        st.error(f"❌ Error: {error_msg}")
                                except:
                                    st.error(f"❌ Error: {error_msg}")
                                    
                                status.update(label="Error", state="error")
                                break
                        
                        # msg is already set above

                        
                        # Check for tool calls
                        if msg.tool_calls:
                            messages.append(msg.to_dict()) 
                            for tool_call in msg.tool_calls:
                                function_name = tool_call.function.name
                                function_args = json.loads(tool_call.function.arguments)
                                
                                # Track consecutive same tool calls
                                if function_name == last_tool_name:
                                    consecutive_same_tool += 1
                                else:
                                    consecutive_same_tool = 0
                                last_tool_name = function_name
                                
                                # Track write_code specifically
                                if function_name == "write_code":
                                    write_code_count += 1
                                
                                st.write(f"🛠️ Executing: `{function_name}`")
                                
                                if function_name in tool_map:
                                     try:
                                         func = tool_map[function_name]
                                         result = func(**function_args)
                                         content = str(result)
                                     except Exception as e:
                                         content = f"Error: {e}"
                                     
                                     messages.append({
                                         "tool_call_id": tool_call.id,
                                         "role": "tool",
                                         "name": function_name,
                                         "content": content
                                     })
                                else:
                                     messages.append({
                                         "tool_call_id": tool_call.id,
                                         "role": "tool",
                                         "name": function_name,
                                         "content": f"Error: Tool {function_name} not found"
                                     })
                        else:
                            content = msg.content
                            full_response = content if content else ""
                            
                            # Parse JSON response if the model returns it as raw JSON
                            if full_response:
                                try:
                                    # Try to parse as JSON (some models return {"content": "...", "tool_calls": [...]})
                                    parsed = json.loads(full_response)
                                    if isinstance(parsed, dict) and "content" in parsed:
                                        full_response = parsed["content"]
                                except (json.JSONDecodeError, TypeError):
                                    pass  # Not JSON, use as-is
                            
                            # Handle empty response (happens when model returns nothing)
                            if not full_response or full_response.strip() == "":
                                # Generate a summary of what was done
                                if write_code_count > 0:
                                    full_response = f"✅ Done! Created {write_code_count} file(s) for your project."
                                else:
                                    full_response = "Task completed."
                            
                            # --- Fallback: Detect Raw Tool Calls in text ---
                            if "write_code(" in full_response or "create_project(" in full_response:
                                st.warning("⚠️ Model outputted raw code. Try Gemini 2.0 Flash for better results.")
                            
                            message_placeholder.markdown(full_response)
                            add_message(current_id, "assistant", full_response)
                            status.update(label="Complete!", state="complete", expanded=False)
                            break 
                            
                    if loop_count >= max_loops:
                        st.error("⚠️ Loop limit reached.")
                        status.update(label="Stopped", state="error")
        
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"Agent error: {e}", exc_info=True)
                    status.update(label="Error", state="error")
