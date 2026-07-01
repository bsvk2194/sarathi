from asyncio import tasks
import os
import shutil
import sqlite3
import dateparser
import requests
from dotenv import load_dotenv
from core.backup import create_backup
from core.memory import LAST_TASK_RESULTS
from flask import jsonify

load_dotenv()

DATABASE = "sarathi.db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# latest note handler  
def handle_latest_note():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT content
        FROM notes
        ORDER BY created_at DESC
        LIMIT 1
        """
    )

    note = cursor.fetchone()

    conn.close()

    if not note:

        return jsonify({
            "reply": "You do not have any notes yet."
        })

    return jsonify({
        "reply":
        f"Latest Note:\n\n{note[0]}"
    })

# storage status handler
def handle_storage_status():

    total, used, free = shutil.disk_usage(os.getcwd())

    used_gb = round(
        used / (1024**3), 2
    )

    free_gb = round(
        free / (1024**3), 2
    )

    return jsonify({
        "reply":
        f"""
    Storage Status

    Used: {used_gb} GB
    Free: {free_gb} GB
    """
    })

# backup count handler
def handle_backup_count():

    if os.name == "nt":
        backup_folder = os.path.join(os.getcwd(), "backups")
    else:
        backup_folder = "/storage/emulated/0/SARATHI_SYNC"

    if os.path.exists(backup_folder):

        backup_count = len([
            f for f in os.listdir(backup_folder)
            if f.startswith("backup_")
            and f.endswith(".db")
        ])

    else:

        backup_count = 0

    return jsonify({
        "reply":
        f"You currently have {backup_count} backups."
    })

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

# search notes handler
def handle_search_notes(keyword):

    keyword = keyword.strip()

    if keyword == "":

        return jsonify({
            "reply":
            "Please tell me what to search for."
        })

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT content
        FROM notes
        WHERE LOWER(content) LIKE ?
        ORDER BY created_at DESC
        """,
        (f"%{keyword.lower()}%",)
    )

    notes = cursor.fetchall()

    conn.close()

    if not notes:

        return jsonify({
            "reply":
            f"No notes found containing '{keyword}'."
        })

    notes_list = ""

    for i, note in enumerate(notes, start=1):

        notes_list += (
            f"{i}. {note[0]}\n\n"
        )

    return jsonify({
        "reply":
        f"""Found {len(notes)} matching note(s).
        {notes_list}
        """
    })

# add note handler
def handle_add_note(note_text):

    note_text = note_text.strip()

    if note_text == "":

        return jsonify({
            "reply": "Please provide a note."
        })

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notes (content)
        VALUES (?)
        """,
        (note_text,)
    )

    conn.commit()

    create_backup()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM notes
        """
    )

    total_notes = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "reply":
        f"""Note saved successfully.

Note:
{note_text}

Total notes: {total_notes}
"""
    })

# upcoming events handler
def handle_upcoming_events():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, event_date
        FROM events
        ORDER BY event_date ASC
        LIMIT 5
        """
    )

    events = cursor.fetchall()

    conn.close()

    if not events:

        return jsonify({
            "reply": "No upcoming events found."
        })

    event_list = ""

    for i, event in enumerate(events, start=1):

        event_list += (
            f"{i}. {event[0]} ({event[1]})\n"
        )

    return jsonify({
        "reply":
        f"Upcoming Events:\n\n{event_list}"
    })

# add event handler
def handle_add_event(title, event_date):

    title = title.strip()
    event_date = event_date.strip()

    #print("Title:", title)
    #print("Date:", event_date)

    if event_date.lower().startswith("next "):
        event_date = event_date[5:]

    parsed_date = dateparser.parse(
        event_date,
        settings={
            "PREFER_DATES_FROM": "future"
        }
    )

    #print("Parsed:", parsed_date)

    if not parsed_date:

        return jsonify({
            "reply":
            "I couldn't understand the date."
        })

    event_date = parsed_date.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO events
        (title, event_date)
        VALUES (?, ?)
        """,
        (
            title,
            event_date
        )
    )

    conn.commit()

    create_backup()

    conn.close()

    return jsonify({
        "reply":
        f"""Event added successfully.

Title:
{title}

Date:
{event_date}
"""
    })

# General chat handler
def handle_general_chat(user_message):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are SARATHI, Karthik's personal AI operating system. "
                    "Be concise, practical and helpful."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:

        return jsonify({
            "reply":
            "I'm having trouble connecting to the language model right now."
        })


    reply = response.json()["choices"][0]["message"]["content"]

    return jsonify({
        "reply": reply
    })

# backup creation handler
def handle_create_backup():

    create_backup()

    return jsonify({
        "reply": "Backup created successfully."
    })