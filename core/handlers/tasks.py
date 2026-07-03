import sqlite3

from flask import jsonify

from core.config import DATABASE
from core.backup import create_backup
from core.memory import set_memory, remember_reply  

# pending tasks handler
def handle_pending_tasks(mode):


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

        set_memory(
            "last_task_results",
            tasks
        )

        conn.close()

        if not tasks:

            return jsonify({
                "reply": "You have no pending tasks."
            })

        task_list = ""

        for i, task in enumerate(tasks, start=1):

            task_list += f"{i}. {task[1]}\n"

        reply = f"Pending Tasks:\n\n{task_list}"

        return remember_reply(reply)

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

        reply = (
    f"You currently have {count} pending tasks. "
    "Would you like to see the list of pending tasks?"
)

        return remember_reply(reply)

    reply = (
    "I couldn't determine whether you wanted "
    "the task list or the task count."
)

    return remember_reply(reply)

# complete task handler
def handle_complete_task(task_name):

    task_name = task_name.strip()

    if task_name == "":

        reply = "Please specify which task to complete."

        return remember_reply(reply)

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

        reply = "I couldn't find a matching pending task."

        return remember_reply(reply)

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

    reply = f"Completed task: {task[1]}"

    return remember_reply(reply)

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

    reply = f"""Task added successfully.

        Task:
        {task_text}

        Pending tasks: {pending_tasks}
        """

    return remember_reply(reply)