import sqlite3

from flask import jsonify

from core.config import DATABASE
from core.backup import create_backup
from core.memory import LAST_TASK_RESULTS

# pending tasks handler
def handle_pending_tasks(mode):

    global LAST_TASK_RESULTS

    if mode == "list":

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, task
            FROM tasks
            WHERE completed = 0
            """
        )

        tasks = cursor.fetchall()

        LAST_TASK_RESULTS.clear()
        LAST_TASK_RESULTS.extend(tasks)

        conn.close()

        if not tasks:

            return jsonify({
                "reply": "You have no pending tasks."
            })

        task_list = ""

        for i, task in enumerate(tasks, start=1):

            task_list += f"{i}. {task[1]}\n"

        return jsonify({
            "reply":
            f"Pending Tasks:\n\n{task_list}"
        })

    elif mode == "count":

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE completed = 0
            """
        )

        count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "reply":
            f"You currently have {count} pending tasks. Would you like to see the list of pending tasks?"
        })

    return jsonify({
        "reply":
        "I couldn't determine whether you wanted the task list or the task count."
    })

# complete task handler
def handle_complete_task(task_name):

    task_name = task_name.strip()

    if task_name == "":

        return jsonify({
            "reply": "Please specify which task to complete."
        })

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, task
        FROM tasks
        WHERE LOWER(task) LIKE ?
        AND completed = 0
        LIMIT 1
        """,
        (f"%{task_name.lower()}%",)
    )

    task = cursor.fetchone()

    if not task:

        conn.close()

        return jsonify({
            "reply": "I couldn't find a matching pending task."
        })

    cursor.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        """,
        (task[0],)
    )

    conn.commit()

    create_backup()

    conn.close()

    return jsonify({
        "reply":
        f"Completed task: {task[1]}"
    })

# add task handler
def handle_add_task(task_text):

    task_text = task_text.strip()

    if task_text == "":

        return jsonify({
            "reply": "Please provide a task."
        })

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (task, completed)
        VALUES (?, ?)
        """,
        (
            task_text,
            0
        )
    )

    conn.commit()

    create_backup()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE completed = 0
        """
    )

    pending_tasks = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "reply":
        f"""Task added successfully.

Task:
{task_text}

Pending tasks: {pending_tasks}
"""
    })