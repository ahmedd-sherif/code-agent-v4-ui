"""
Code Writer Tool - Generates and edits code files.
Now integrated with Project Manager for automatic project context.
"""

import os
from pathlib import Path
from .project_manager import get_project_path_for_tools, save_progress


def write_code(
    filename: str,
    code_content: str,
    description: str = "",
    subdirectory: str = ""
) -> dict:
    """
    Write code to a new file in the current project folder.
    
    Args:
        filename: Name of the file to create (e.g., 'main.py', 'index.html')
        code_content: The actual code content to write to the file
        description: Brief description of what this code does
        subdirectory: Optional subdirectory within the project (e.g., 'src', 'components')
    
    Returns:
        dict: Status with success/error message and file path
    """
    try:
        # Get current project path
        project_path = get_project_path_for_tools()
        
        if project_path:
            # Use project folder
            if subdirectory:
                dir_path = project_path / subdirectory
            else:
                dir_path = project_path
        else:
            # Fallback to current directory if no project is active
            if subdirectory:
                dir_path = Path(subdirectory)
            else:
                dir_path = Path(".")
        
        # Ensure directory exists
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = dir_path / filename
        
        # Write the code
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        # Save progress if in a project
        if project_path:
            save_progress(
                notes=f"Created file: {filename}" + (f" - {description}" if description else ""),
                files_changed=[filename]
            )
        
        return {
            "status": "success",
            "message": f"Successfully created file: {file_path}",
            "file_path": str(file_path.absolute()),
            "description": description,
            "in_project": project_path is not None
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to write code: {str(e)}"
        }


def edit_code(
    filepath: str,
    old_content: str,
    new_content: str,
    description: str = ""
) -> dict:
    """
    Edit an existing code file by replacing specific content.
    
    Args:
        filepath: Path to the file to edit (relative to project or absolute)
        old_content: The exact content to find and replace
        new_content: The new content to replace with
        description: Brief description of what this edit does
    
    Returns:
        dict: Status with success/error message
    """
    try:
        # Check if it's a relative path and we have a project
        project_path = get_project_path_for_tools()
        
        file_path = Path(filepath)
        if not file_path.is_absolute() and project_path:
            file_path = project_path / filepath
        
        if not file_path.exists():
            return {
                "status": "error",
                "error_message": f"File not found: {filepath}"
            }
        
        # Read current content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if old content exists
        if old_content not in content:
            return {
                "status": "error",
                "error_message": "The specified content to replace was not found in the file"
            }
        
        # Replace content
        new_file_content = content.replace(old_content, new_content, 1)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_file_content)
        
        # Save progress if in a project
        if project_path:
            save_progress(
                notes=f"Edited file: {file_path.name}" + (f" - {description}" if description else ""),
                files_changed=[file_path.name]
            )
        
        return {
            "status": "success",
            "message": f"Successfully edited file: {filepath}",
            "description": description
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to edit code: {str(e)}"
        }
