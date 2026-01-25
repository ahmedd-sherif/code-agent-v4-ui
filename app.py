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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page Config
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

# --- Sidebar ---
with st.sidebar:
    st.title("🗂️ Sessions")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_session_id = str(uuid.uuid4())
        create_session(st.session_state.current_session_id, "New Session")
        st.rerun()

    st.divider()
    
    # Web Search Toggle
    use_web_search = st.toggle("🌐 Enable Web Search (Tavily)", value=True, help="Turn on to allow the agent to search the internet.")
    
    st.divider()
    
    sessions = list_sessions()
    for sess in sessions:
        label = sess.get("name", "Untitled") or "Untitled"
        # Truncate label
        if len(label) > 20: label = label[:17] + "..."
        if st.button(f"📄 {label}", key=sess["session_id"], use_container_width=True):
            st.session_state.current_session_id = sess["session_id"]
            st.rerun()

# --- Main Interface ---
st.title("🤖 Code Agent Workspace")

# Session State Init
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())
    create_session(st.session_state.current_session_id, "New Session")

current_id = st.session_state.current_session_id

# Load History
# History from DB is list of dicts: {'role': 'user', 'content': '...'}
history = get_session_history(current_id)

# Display Messages
for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("What would you like to build?"):
    # 1. User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    add_message(current_id, "user", prompt)
    
    # Reload history to include new message
    history = get_session_history(current_id)

    # 2. Agent Loop
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Filter tools based on toggle
        current_tools = [t for t in available_tools if t != web_search] # Remove search first
        if use_web_search:
            current_tools.append(web_search) # Add back if enabled
        
        # Construct messages for LLM
        # System instruction first
        current_system_instruction = SYSTEM_INSTRUCTION
        if use_web_search:
             current_system_instruction += "\n\nIMPORTANT: Web Search is ENABLED. You MUST use the `web_search` tool if you need external information."
        
        messages = [{"role": "system", "content": current_system_instruction}]
        # Append history
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
            
        try:
            # We run a loop to handle tool calls
            while True:
                response = completion(
                    # model="openrouter/mistralai/devstral-2512:free",
                    model="gemini/gemini-2.0-flash-exp", # Using Gemini for better tool use
                    messages=messages,
                    tools=current_tools,
                    tool_choice="auto" 
                )
                
                msg = response.choices[0].message
                
                # Check for tool calls
                if msg.tool_calls:
                    messages.append(msg) # Add assistant message with tool calls
                    
                    # Execute tools
                    for tool_call in msg.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Execute
                        if function_name in tool_map:
                             # Notify UI
                             message_placeholder.markdown(f"*Executing {function_name}...*")
                             
                             try:
                                 func = tool_map[function_name]
                                 result = func(**function_args)
                                 content = str(result)
                             except Exception as e:
                                 content = f"Error: {e}"
                             
                             # Add tool output to messages
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
                    # Final response
                    content = msg.content
                    full_response = content
                    message_placeholder.markdown(full_response)
                    
                    # Save assistant response to DB
                    add_message(current_id, "assistant", full_response)
                    break 

        except Exception as e:
            st.error(f"Error: {e}")
            logger.error(f"Agent error: {e}", exc_info=True)
