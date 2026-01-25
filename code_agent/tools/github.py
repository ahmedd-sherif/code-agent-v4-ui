"""
GitHub Tool - Create repositories and push code to GitHub.
Requires GITHUB_TOKEN environment variable.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


def _get_github_client():
    """Get authenticated GitHub client."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None, "GITHUB_TOKEN environment variable is not set. Please provide your GitHub Personal Access Token."
    
    if not GITHUB_AVAILABLE:
        return None, "PyGithub library is not installed. Run: pip install PyGithub"
    
    return Github(token), None


def create_repository(
    name: str,
    description: str = "",
    private: bool = False,
    auto_init: bool = True
) -> dict:
    """
    Create a new GitHub repository.
    
    Args:
        name: Name of the repository to create
        description: Repository description (optional)
        private: Whether the repository should be private (default: False/public)
        auto_init: Whether to initialize with a README (default: True)
    
    Returns:
        dict: Status with repository URL or error message
    """
    client, error = _get_github_client()
    if error:
        return {"status": "error", "error_message": error}
    
    try:
        user = client.get_user()
        
        # Check if repo already exists
        try:
            existing_repo = user.get_repo(name)
            return {
                "status": "error",
                "error_message": f"Repository '{name}' already exists at {existing_repo.html_url}"
            }
        except:
            pass  # Repo doesn't exist, we can create it
        
        # Create the repository
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init
        )
        
        return {
            "status": "success",
            "message": f"Successfully created repository: {name}",
            "repository_url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
            "private": repo.private
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create repository: {str(e)}"
        }


def push_code(
    repository_name: str,
    local_path: str,
    commit_message: str = "Initial commit",
    branch: str = "main"
) -> dict:
    """
    Push local code to a GitHub repository.
    
    Args:
        repository_name: Name of the GitHub repository (must exist)
        local_path: Local path to the code to push
        commit_message: Commit message (default: "Initial commit")
        branch: Branch to push to (default: "main")
    
    Returns:
        dict: Status with success/error message
    """
    client, error = _get_github_client()
    if error:
        return {"status": "error", "error_message": error}
    
    try:
        local_dir = Path(local_path)
        
        if not local_dir.exists():
            return {
                "status": "error",
                "error_message": f"Local path not found: {local_path}"
            }
        
        # Get repository info
        user = client.get_user()
        try:
            repo = user.get_repo(repository_name)
        except:
            return {
                "status": "error",
                "error_message": f"Repository '{repository_name}' not found. Create it first using create_repository."
            }
        
        remote_url = repo.clone_url
        # Add token to URL for authentication
        token = os.getenv("GITHUB_TOKEN")
        auth_url = remote_url.replace("https://", f"https://{token}@")
        
        # Initialize git if needed
        git_dir = local_dir / ".git"
        if not git_dir.exists():
            subprocess.run(["git", "init"], cwd=local_dir, capture_output=True)
        
        # Configure git user if not set
        subprocess.run(
            ["git", "config", "user.email", "code-agent@local"],
            cwd=local_dir, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Code Agent"],
            cwd=local_dir, capture_output=True
        )
        
        # Add all files
        subprocess.run(["git", "add", "."], cwd=local_dir, capture_output=True)
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=local_dir, capture_output=True, text=True
        )
        
        # Add remote if not exists
        subprocess.run(
            ["git", "remote", "remove", "origin"],
            cwd=local_dir, capture_output=True
        )
        subprocess.run(
            ["git", "remote", "add", "origin", auth_url],
            cwd=local_dir, capture_output=True
        )
        
        # Push
        push_result = subprocess.run(
            ["git", "push", "-u", "origin", branch, "--force"],
            cwd=local_dir, capture_output=True, text=True
        )
        
        if push_result.returncode != 0:
            return {
                "status": "error",
                "error_message": f"Failed to push: {push_result.stderr}"
            }
        
        return {
            "status": "success",
            "message": f"Successfully pushed code to {repo.html_url}",
            "repository_url": repo.html_url,
            "branch": branch,
            "commit_message": commit_message
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to push code: {str(e)}"
        }
