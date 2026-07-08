import sqlite3

from core.config import DATABASE
from core.backup import create_backup

def remember(content):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO memories (content)
        VALUES (?)
        """,
        (content,)
    )

    conn.commit()

    create_backup()

    conn.close()

def get_all_memories():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, content
        FROM memories
        ORDER BY created_at DESC
        """
    )

    memories = cursor.fetchall()

    conn.close()

    return memories

def search_memories(query):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, content
        FROM memories
        WHERE LOWER(content) LIKE ?
        ORDER BY created_at DESC
        """,
        (f"%{query.lower()}%",)
    )

    memories = cursor.fetchall()

    conn.close()

    return memories

def forget_memory(memory_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    conn.commit()

    create_backup()

    conn.close()