from git import Repo, GitCommandError
import os
import logging
from typing import Optional, List, Dict

# Logger setup
logger = logging.getLogger(__name__)

def clone_repository(repo_url: str, target_path: str) -> str:
    """
    Clones a git repository to a local path.
    Ref: https://git-scm.com/docs/git-clone
    
    Args:
        repo_url: URL of the repository to clone.
        target_path: Local directory path to clone into.
        
    Returns:
        Status message string.
    """
    try:
        # Inject token if present and not already in URL
        token = os.getenv("GITHUB_TOKEN")
        if token and "github.com" in repo_url and "@" not in repo_url:
             auth_url = repo_url.replace("https://", f"https://{token}@")
        else:
            auth_url = repo_url

        Repo.clone_from(auth_url, target_path)
        return f"Successfully cloned {repo_url} to {target_path}"
    except GitCommandError as e:
        return f"Error cloning repository: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def git_status(repo_path: str) -> str:
    """
    Gets the git status of a repository.
    
    Args:
        repo_path: Path to the local git repository.
        
    Returns:
        String representation of git status.
    """
    try:
        repo = Repo(repo_path)
        return repo.git.status()
    except Exception as e:
        return f"Error getting status: {e}"

def git_add_all(repo_path: str) -> str:
    """
    Stages all changes in the repository.
    
    Args:
        repo_path: Path to the local git repository.
    """
    try:
        repo = Repo(repo_path)
        repo.git.add('.')
        return "Successfully staged all changes."
    except Exception as e:
        return f"Error staging changes: {e}"

def git_commit(repo_path: str, message: str) -> str:
    """
    Commits staged changes.
    
    Args:
        repo_path: Path to the local git repository.
        message: Commit message.
    """
    try:
        repo = Repo(repo_path)
        repo.index.commit(message)
        return f"Successfully committed with message: {message}"
    except Exception as e:
        return f"Error committing: {e}"

def git_push(repo_path: str, branch: str = "main") -> str:
    """
    Pushes commits to the remote repository.
    
    Args:
        repo_path: Path to the local git repository.
        branch: Branch name to push to.
    """
    try:
        repo = Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.push(refspec=f"{branch}:{branch}")
        return f"Successfully pushed to {branch}"
    except Exception as e:
        return f"Error pushing: {e}"

def git_pull(repo_path: str) -> str:
    """
    Pulls latest changes from remote.
    """
    try:
        repo = Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.pull()
        return "Successfully pulled latest changes."
    except Exception as e:
        return f"Error pulling: {e}"
