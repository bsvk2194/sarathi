import sqlite3

from core.config import DATABASE
from core.backup import create_backup
from core.llm import find_similar_memories, retrieve_memory_numbers, reason_over_memories, find_contradicting_memory_numbers

def remember(content, importance = 1):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (content, importance)
        VALUES (?, ?)
        """,
        (content, importance)
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

def retrieve_semantic_memories(query):

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

    memory_numbers = retrieve_memory_numbers(
        query,
        memories
    )
    relevant_memories = []

    for number in memory_numbers:

        if 1 <= number <= len(memories):

            relevant_memories.append(
                memories[number - 1]
            )

    memory_ids = [memory[0] for memory in relevant_memories]

    increment_memory_usage_batch(memory_ids)
    update_memory_importance_batch(memory_ids)

    return relevant_memories

def find_duplicate_memories(content):

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

    if not memories:

        return []
    
    memory_numbers = find_similar_memories(
        content,
        memories
    )

    duplicates = []

    for number in memory_numbers:

        if 1 <= number <= len(memories):

            duplicates.append(
                memories[number - 1]
            )

    return duplicates

def answer_from_memories(question):

    memories = retrieve_semantic_memories(question)

    if not memories:

        return None

    answer = reason_over_memories(
        question,
        memories
    )

    return answer, memories

'''def increment_memory_usage(memory_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE memories
        SET usage_count = usage_count + 1
        WHERE id = ?
        """,
        (memory_id,)
    )

    conn.commit()
    conn.close()'''

def increment_memory_usage_batch(memory_ids):

    if not memory_ids:
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.executemany(
        """
        UPDATE memories
        SET
            usage_count = usage_count + 1,
            last_accessed = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        [(memory_id,) for memory_id in memory_ids]
    )

    conn.commit()
    conn.close()

'''def update_memory_importance(memory_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT usage_count, importance
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return

    usage_count, current_importance = result

    if usage_count >= 25:
        new_importance = 3

    elif usage_count >= 10:
        new_importance = 2

    else:
        new_importance = 1

    if new_importance != current_importance:

        cursor.execute(
            """
            UPDATE memories
            SET importance = ?
            WHERE id = ?
            """,
            (new_importance, memory_id)
        )

        conn.commit()

    conn.close()'''

def update_memory_importance_batch(memory_ids):

    if not memory_ids:
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for memory_id in memory_ids:

        cursor.execute(
            """
            SELECT usage_count, importance
            FROM memories
            WHERE id = ?
            """,
            (memory_id,)
        )

        result = cursor.fetchone()

        if result is None:
            continue

        usage_count, current_importance = result

        if usage_count >= 25:
            new_importance = 3

        elif usage_count >= 10:
            new_importance = 2

        else:
            new_importance = 1

        if new_importance != current_importance:

            cursor.execute(
                """
                UPDATE memories
                SET importance = ?
                WHERE id = ?
                """,
                (new_importance, memory_id)
            )

    conn.commit()
    conn.close()

def find_contradicting_memories(content):

    memories = retrieve_semantic_memories(content)

    memory_numbers = find_contradicting_memory_numbers(
        content,
        memories
    )

    contradicting_memories = []

    for number in memory_numbers:

        if 1 <= number <= len(memories):

            contradicting_memories.append(
                memories[number - 1]
            )

    return contradicting_memories