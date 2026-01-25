"""
Project Manager Tool - Manages projects in the Created Programs folder.
Each project gets its own folder with metadata tracking.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Base directory for all projects
PROJECTS_BASE_DIR = Path(__file__).parent.parent.parent / "Created Programs"

# Current project context (stored in memory during session)
_current_project: Optional[str] = None


def _ensure_base_dir():
    """Ensure the Created Programs directory exists."""
    PROJECTS_BASE_DIR.mkdir(parents=True, exist_ok=True)


def _get_project_path(project_name: str) -> Path:
    """Get the full path to a project folder."""
    return PROJECTS_BASE_DIR / project_name


def _get_project_metadata_path(project_name: str) -> Path:
    """Get the path to project metadata file."""
    return _get_project_path(project_name) / ".project.json"


def _load_project_metadata(project_name: str) -> Optional[dict]:
    """Load project metadata from .project.json"""
    meta_path = _get_project_metadata_path(project_name)
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def _save_project_metadata(project_name: str, metadata: dict):
    """Save project metadata to .project.json"""
    meta_path = _get_project_metadata_path(project_name)
    metadata['updated_at'] = datetime.now().isoformat()
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def create_project(name: str, description: str = "") -> dict:
    """
    Create a new project with its own folder.
    
    Args:
        name: Project name (will be used as folder name, use lowercase with hyphens)
        description: Brief description of the project
    
    Returns:
        dict: Status with project path and info
    """
    global _current_project
    _ensure_base_dir()
    
    # Sanitize project name
    safe_name = name.lower().replace(' ', '-').replace('_', '-')
    project_path = _get_project_path(safe_name)
    
    if project_path.exists():
        return {
            "status": "error",
            "error_message": f"Project '{safe_name}' already exists. Use switch_project() to work on it."
        }
    
    try:
        # Create project folder
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file
        metadata = {
            "name": safe_name,
            "display_name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "in_progress",
            "files": [],
            "progress": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "Project created"
                }
            ]
        }
        _save_project_metadata(safe_name, metadata)
        
        # Set as current project
        _current_project = safe_name
        
        return {
            "status": "success",
            "message": f"Created project '{name}'",
            "project_name": safe_name,
            "project_path": str(project_path.absolute()),
            "description": description
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create project: {str(e)}"
        }


def list_projects() -> dict:
    """
    List all projects in the Created Programs folder.
    
    Returns:
        dict: List of all projects with their status
    """
    global _current_project
    _ensure_base_dir()
    
    projects = []
    for item in PROJECTS_BASE_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            metadata = _load_project_metadata(item.name)
            if metadata:
                projects.append({
                    "name": item.name,
                    "display_name": metadata.get("display_name", item.name),
                    "description": metadata.get("description", ""),
                    "status": metadata.get("status", "unknown"),
                    "created_at": metadata.get("created_at", ""),
                    "updated_at": metadata.get("updated_at", ""),
                    "file_count": len(metadata.get("files", [])),
                    "is_current": item.name == _current_project
                })
            else:
                # Folder exists but no metadata
                projects.append({
                    "name": item.name,
                    "display_name": item.name,
                    "description": "No metadata found",
                    "status": "unknown",
                    "is_current": item.name == _current_project
                })
    
    return {
        "status": "success",
        "projects": projects,
        "total_count": len(projects),
        "current_project": _current_project
    }


def switch_project(project_name: str) -> dict:
    """
    Switch to a different project. All file operations will happen in this project's folder.
    
    Args:
        project_name: Name of the project to switch to
    
    Returns:
        dict: Status and project info
    """
    global _current_project
    _ensure_base_dir()
    
    safe_name = project_name.lower().replace(' ', '-').replace('_', '-')
    project_path = _get_project_path(safe_name)
    
    if not project_path.exists():
        return {
            "status": "error",
            "error_message": f"Project '{project_name}' not found. Use list_projects() to see available projects."
        }
    
    _current_project = safe_name
    metadata = _load_project_metadata(safe_name)
    
    # Add switch action to progress
    if metadata:
        metadata.setdefault("progress", []).append({
            "timestamp": datetime.now().isoformat(),
            "action": "Switched to project"
        })
        _save_project_metadata(safe_name, metadata)
    
    return {
        "status": "success",
        "message": f"Switched to project '{project_name}'",
        "project_name": safe_name,
        "project_path": str(project_path.absolute()),
        "description": metadata.get("description", "") if metadata else "",
        "files": metadata.get("files", []) if metadata else []
    }


def get_current_project() -> dict:
    """
    Get information about the current active project.
    
    Returns:
        dict: Current project info or message if no project is active
    """
    global _current_project
    
    if not _current_project:
        return {
            "status": "info",
            "message": "No project is currently active. Use create_project() or switch_project() first.",
            "current_project": None
        }
    
    project_path = _get_project_path(_current_project)
    metadata = _load_project_metadata(_current_project)
    
    return {
        "status": "success",
        "current_project": _current_project,
        "project_path": str(project_path.absolute()),
        "metadata": metadata
    }


def save_progress(notes: str, files_changed: list = None) -> dict:
    """
    Save progress notes for the current project.
    
    Args:
        notes: Description of what was done
        files_changed: Optional list of files that were changed
    
    Returns:
        dict: Status
    """
    global _current_project
    
    if not _current_project:
        return {
            "status": "error",
            "error_message": "No project is currently active. Use create_project() or switch_project() first."
        }
    
    metadata = _load_project_metadata(_current_project)
    if not metadata:
        return {
            "status": "error",
            "error_message": "Project metadata not found."
        }
    
    # Add progress entry
    progress_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": notes
    }
    if files_changed:
        progress_entry["files"] = files_changed
    
    metadata.setdefault("progress", []).append(progress_entry)
    
    # Update files list if provided
    if files_changed:
        existing_files = set(metadata.get("files", []))
        existing_files.update(files_changed)
        metadata["files"] = list(existing_files)
    
    _save_project_metadata(_current_project, metadata)
    
    return {
        "status": "success",
        "message": f"Progress saved for project '{_current_project}'",
        "notes": notes
    }


def get_project_path_for_tools() -> Optional[Path]:
    """
    Helper function for other tools to get the current project path.
    Returns None if no project is active.
    """
    global _current_project
    if _current_project:
        return _get_project_path(_current_project)
    return None


def get_project_history(project_name: str = None) -> dict:
    """
    Get the progress history of a project.
    
    Args:
        project_name: Project name (uses current project if not specified)
    
    Returns:
        dict: Project history and progress
    """
    global _current_project
    
    name = project_name or _current_project
    if not name:
        return {
            "status": "error",
            "error_message": "No project specified and no project is currently active."
        }
    
    safe_name = name.lower().replace(' ', '-').replace('_', '-')
    metadata = _load_project_metadata(safe_name)
    
    if not metadata:
        return {
            "status": "error",
            "error_message": f"Project '{name}' not found or has no metadata."
        }
    
    return {
        "status": "success",
        "project_name": safe_name,
        "description": metadata.get("description", ""),
        "created_at": metadata.get("created_at", ""),
        "updated_at": metadata.get("updated_at", ""),
        "status": metadata.get("status", "unknown"),
        "files": metadata.get("files", []),
        "progress": metadata.get("progress", [])
    }
