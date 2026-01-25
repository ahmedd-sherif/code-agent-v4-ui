import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Constants
DB_PATH = Path(__file__).parent / "memory.db"

# Logger
logger = logging.getLogger(__name__)

def _get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database tables."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        name TEXT,
        created_at TEXT,
        last_active TEXT
    )
    """)
    
    # Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
    )
    """)
    
    conn.commit()
    conn.close()

def create_session(session_id: str, name: str = "New Session"):
    """Create a new session."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO sessions (session_id, name, created_at, last_active) VALUES (?, ?, ?, ?)",
            (session_id, name, now, now)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # Session already exists
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return False

def add_message(session_id: str, role: str, content: str):
    """Add a message to the session history."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        # Insert message
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, now)
        )
        
        # Update session touch time
        cursor.execute(
            "UPDATE sessions SET last_active = ? WHERE session_id = ?",
            (now, session_id)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error adding message: {e}")

def get_session_history(session_id: str, limit: int = 50) -> List[Dict]:
    """Get the recent history for a session."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        # Return reversed to be chronological
        history = [dict(row) for row in rows]
        return history[::-1]
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return []

def list_sessions() -> List[Dict]:
    """List all sessions ordered by activity."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY last_active DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return []
        
# Initialize on load
init_db()
