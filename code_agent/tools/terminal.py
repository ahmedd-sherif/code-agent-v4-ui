"""
Terminal Tool - Runs shell commands safely.
Now integrated with Project Manager for automatic project context.
"""

import subprocess
import os
from typing import Optional
from .project_manager import get_project_path_for_tools, save_progress


# Commands that are potentially dangerous and should be warned about
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "rm -rf ~",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",  # Fork bomb
    "> /dev/sda",
    "chmod -R 777 /",
]


def run_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout_seconds: int = 120
) -> dict:
    """
    Execute a shell command and return the output.
    If no working_directory is specified, uses the current project folder.
    
    Args:
        command: The command to execute (e.g., 'pip install requests', 'npm install')
        working_directory: Directory to run the command in (default: current project folder)
        timeout_seconds: Maximum time to wait for the command to complete (default: 120)
    
    Returns:
        dict: Status with command output or error message
    """
    # Safety check for dangerous commands
    command_lower = command.lower()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command_lower:
            return {
                "status": "error",
                "error_message": f"This command appears to be dangerous and was blocked: {command}"
            }
    
    try:
        # Determine working directory
        if working_directory:
            cwd = working_directory
        else:
            # Use project folder if available
            project_path = get_project_path_for_tools()
            if project_path:
                cwd = str(project_path)
            else:
                cwd = os.getcwd()
        
        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        
        output = result.stdout
        error_output = result.stderr
        
        # Save progress if in a project and command succeeded
        project_path = get_project_path_for_tools()
        if project_path and result.returncode == 0:
            save_progress(
                notes=f"Ran command: {command[:50]}{'...' if len(command) > 50 else ''}"
            )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Command executed successfully",
                "command": command,
                "output": output if output else "(no output)",
                "working_directory": cwd
            }
        else:
            return {
                "status": "error",
                "error_message": f"Command failed with exit code {result.returncode}",
                "command": command,
                "output": output,
                "error_output": error_output,
                "working_directory": cwd
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error_message": f"Command timed out after {timeout_seconds} seconds",
            "command": command
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to execute command: {str(e)}",
            "command": command
        }
