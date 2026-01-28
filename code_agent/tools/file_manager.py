"""
File Manager Tool - Create, read, delete files and list directories.
"""

import os
from pathlib import Path
from typing import Optional



def _resolve_path(filepath: str, base_path: str = None) -> Optional[Path]:
    """Resolve and validate path relative to base_path if provided."""
    path = Path(filepath)
    if base_path:
        # If relative, append to base_path. If absolute, we might need to strip or check.
        # Simplest: Force relative resolution if base_path is key
        # If filepath is "C:/foo", and base is "D:/bar", we ignore base? No.
        # We assume filepath is relative to base, or if absolute, must be inside base.
        
        base = Path(base_path).resolve()
        if path.is_absolute():
            # Check if it starts with base
            full_path = path.resolve()
        else:
            full_path = (base / path).resolve()
            
        # Security Check
        try:
              full_path.relative_to(base)
        except ValueError:
             return None # Path traversal attempt or outside base
             
        return full_path
    
    return Path(filepath)


def create_file(
    filepath: str,
    content: str = "",
    overwrite: bool = False,
    base_path: str = None
) -> dict:
    """
    Create a new file with optional content.
    
    Args:
        filepath: Path where the file should be created (relative to base_path if provided)
        content: Content to write to the file (default: empty)
        overwrite: Whether to overwrite if exists (default: False)
        base_path: Optional base directory to restrict operations to
    
    Returns:
        dict: Status
    """
    try:
        file_path = _resolve_path(filepath, base_path)
        if not file_path:
             return {"status": "error", "error_message": f"Access denied: Path {filepath} is outside base directory."}
        
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


def read_file(filepath: str, base_path: str = None) -> dict:
    """
    Read the contents of a file.
    
    Args:
        filepath: Path to the file to read
        base_path: Optional base directory
    """
    try:
        file_path = _resolve_path(filepath, base_path)
        if not file_path:
             return {"status": "error", "error_message": f"Access denied: Path {filepath} is outside base directory."}
        
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


def delete_file(filepath: str, base_path: str = None) -> dict:
    """
    Delete a file.
    
    Args:
        filepath: Path to the file to delete
        base_path: Optional base directory
    """
    try:
        file_path = _resolve_path(filepath, base_path)
        if not file_path:
             return {"status": "error", "error_message": f"Access denied: Path {filepath} is outside base directory."}
        
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


def list_directory(directory: str = ".", base_path: str = None) -> dict:
    """
    List contents of a directory.
    
    Args:
        directory: Path to the directory to list (default: current directory or root of base_path)
        base_path: Optional base directory
    """
    try:
        if directory == "." and base_path:
             # If base_path provided and dir is ".", verify against base_path
             # _resolve_path will handle "." relative to base_path
             pass
             
        dir_path = _resolve_path(directory, base_path)
        if not dir_path:
             return {"status": "error", "error_message": f"Access denied: Path {directory} is outside base directory."}
        
        if not dir_path.exists():
            # If default "." led to root, it might be fine, but if specific path missing:
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
