"""
File Manager Tool - Create, read, delete files and list directories.
"""

import os
from pathlib import Path
from typing import Optional


def create_file(
    filepath: str,
    content: str = "",
    overwrite: bool = False
) -> dict:
    """
    Create a new file with optional content.
    
    Args:
        filepath: Full path where the file should be created
        content: Content to write to the file (default: empty)
        overwrite: Whether to overwrite if file exists (default: False)
    
    Returns:
        dict: Status with success/error message
    """
    try:
        file_path = Path(filepath)
        
        # Check if file exists
        if file_path.exists() and not overwrite:
            return {
                "status": "error",
                "error_message": f"File already exists: {filepath}. Set overwrite=True to replace it."
            }
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"Successfully created file: {filepath}",
            "file_path": str(file_path.absolute())
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create file: {str(e)}"
        }


def read_file(filepath: str) -> dict:
    """
    Read the contents of a file.
    
    Args:
        filepath: Path to the file to read
    
    Returns:
        dict: Status with file content or error message
    """
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            return {
                "status": "error",
                "error_message": f"File not found: {filepath}"
            }
        
        if not file_path.is_file():
            return {
                "status": "error",
                "error_message": f"Path is not a file: {filepath}"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "file_path": str(file_path.absolute()),
            "content": content,
            "size_bytes": file_path.stat().st_size
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to read file: {str(e)}"
        }


def delete_file(filepath: str) -> dict:
    """
    Delete a file.
    
    Args:
        filepath: Path to the file to delete
    
    Returns:
        dict: Status with success/error message
    """
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            return {
                "status": "error",
                "error_message": f"File not found: {filepath}"
            }
        
        if not file_path.is_file():
            return {
                "status": "error",
                "error_message": f"Path is not a file: {filepath}. Use rmdir for directories."
            }
        
        file_path.unlink()
        
        return {
            "status": "success",
            "message": f"Successfully deleted file: {filepath}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to delete file: {str(e)}"
        }


def list_directory(directory: str = ".") -> dict:
    """
    List contents of a directory.
    
    Args:
        directory: Path to the directory to list (default: current directory)
    
    Returns:
        dict: Status with list of files and directories
    """
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {
                "status": "error",
                "error_message": f"Directory not found: {directory}"
            }
        
        if not dir_path.is_dir():
            return {
                "status": "error",
                "error_message": f"Path is not a directory: {directory}"
            }
        
        items = []
        for item in dir_path.iterdir():
            item_info = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": str(item.absolute())
            }
            if item.is_file():
                item_info["size_bytes"] = item.stat().st_size
            items.append(item_info)
        
        # Sort: directories first, then files, alphabetically
        items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return {
            "status": "success",
            "directory": str(dir_path.absolute()),
            "items": items,
            "total_count": len(items)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to list directory: {str(e)}"
        }
