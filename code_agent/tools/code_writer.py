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
    subdirectory: str = "",
    base_path: str = None
) -> dict:
    """
    Write code to a new file.
    
    Args:
        filename: Name of the file to create
        code_content: Code to write
        description: Description
        subdirectory: Subdirectory
        base_path: Optional base directory (workspace path)
    """
    try:
        # Determine root: base_path > get_project_path() > current dir
        project_path = None
        if base_path:
             project_path = Path(base_path)
        else:
             project_path = get_project_path_for_tools()
        
        if project_path:
            target_dir = project_path / subdirectory if subdirectory else project_path
        else:
            target_dir = Path(subdirectory) if subdirectory else Path(".")
            
        # Ensure directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = target_dir / filename
        
        # Write
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        # Save progress if we have a project context (global or passed)
        # Note: If base_path is passed, save_progress logic might fail if it relies on global state
        # For now, we only save progress if using the global project manager flow, or if we update save_progress too.
        # We'll skip save_progress for isolated sessions for now to avoid complexity, or try it safely.
        if get_project_path_for_tools(): # Only if global context exists
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
    description: str = "",
    base_path: str = None
) -> dict:
    """
    Edit an existing code file.
    
    Args:
        filepath: Path to file
        old_content: Content to find
        new_content: Replacement
        description: Description
        base_path: Optional base directory
    """
    try:
        # Resolve path
        project_path = None
        if base_path:
             project_path = Path(base_path)
        else:
             project_path = get_project_path_for_tools()
             
        file_path = Path(filepath)
        if not file_path.is_absolute() and project_path:
            file_path = project_path / filepath
            
        if not file_path.exists():
            return {
                "status": "error",
                "error_message": f"File not found: {filepath}"
            }
        
        # Read
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if old_content not in content:
            return {
                "status": "error",
                "error_message": "The specified content to replace was not found in the file"
            }
            
        new_file_content = content.replace(old_content, new_content, 1)
        
        # Write
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_file_content)
            
        if get_project_path_for_tools():
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
