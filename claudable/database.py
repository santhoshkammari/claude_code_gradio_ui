import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class ChatDatabase:
    def __init__(self, db_path: str = "chats.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_uuid TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_uuid) REFERENCES chats(uuid)
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_chat_uuid
            ON messages(chat_uuid)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chats_updated_at
            ON chats(updated_at DESC)
        """)

        conn.commit()
        conn.close()

    def create_chat(self, title: Optional[str] = None) -> str:
        """Create a new chat session and return its UUID"""
        chat_uuid = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO chats (uuid, title) VALUES (?, ?)",
            (chat_uuid, title or "New Chat")
        )

        conn.commit()
        conn.close()
        return chat_uuid

    def get_chat(self, chat_uuid: str) -> Optional[Dict]:
        """Get a chat by UUID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM chats WHERE uuid = ?",
            (chat_uuid,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_chats(self) -> List[Dict]:
        """Get all chats ordered by updated_at DESC"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM chats ORDER BY updated_at DESC"
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_chat_title(self, chat_uuid: str, title: str):
        """Update chat title"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE chats SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE uuid = ?",
            (title, chat_uuid)
        )

        conn.commit()
        conn.close()

    def add_message(self, chat_uuid: str, role: str, content: str):
        """Add a message to a chat"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (chat_uuid, role, content) VALUES (?, ?, ?)",
            (chat_uuid, role, content)
        )

        # Update chat's updated_at timestamp
        cursor.execute(
            "UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE uuid = ?",
            (chat_uuid,)
        )

        conn.commit()
        conn.close()

    def get_messages(self, chat_uuid: str) -> List[Dict]:
        """Get all messages for a chat"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM messages WHERE chat_uuid = ? ORDER BY created_at ASC",
            (chat_uuid,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_chat(self, chat_uuid: str):
        """Delete a chat and all its messages"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM messages WHERE chat_uuid = ?", (chat_uuid,))
        cursor.execute("DELETE FROM chats WHERE uuid = ?", (chat_uuid,))

        conn.commit()
        conn.close()

    def generate_title_from_message(self, message: str, max_length: int = 50) -> str:
        """Generate a chat title from the first message"""
        # Take first line or first max_length characters
        title = message.split('\n')[0]
        if len(title) > max_length:
            title = title[:max_length].rsplit(' ', 1)[0] + '...'
        return title or "New Chat"
