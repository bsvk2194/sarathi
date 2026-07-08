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

    # Retrieve the memory before deleting it
    cursor.execute(
        """
        SELECT content
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    if not memory:

        conn.close()

        return None

    # Delete the memory
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

    return memory[0]

def forget_memories(query):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, content
        FROM memories
        WHERE LOWER(content) LIKE ?
        """,
        (f"%{query.lower()}%",)
    )

    memories = cursor.fetchall()

    if not memories:

        conn.close()

        return []

    cursor.execute(
        """
        DELETE FROM memories
        WHERE LOWER(content) LIKE ?
        """,
        (f"%{query.lower()}%",)
    )

    conn.commit()

    create_backup()

    conn.close()

    return memories

def update_memory(query, replacement):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, content
        FROM memories
        WHERE LOWER(content) LIKE ?
        LIMIT 1
        """,
        (f"%{query.lower()}%",)
    )

    memory = cursor.fetchone()

    if not memory:

        conn.close()

        return None

    updated_content = memory[1].replace(
        query,
        replacement
    )

    cursor.execute(
        """
        UPDATE memories
        SET content = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            updated_content,
            memory[0]
        )
    )

    conn.commit()

    create_backup()

    conn.close()

    return (
        memory[1],
        updated_content
    )

def update_memory_by_id(memory_id, new_content):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT content
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    if not memory:

        conn.close()

        return None

    cursor.execute(
        """
        UPDATE memories
        SET content = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            new_content,
            memory_id
        )
    )

    conn.commit()

    create_backup()

    conn.close()

    return (
        memory[0],
        new_content
    )