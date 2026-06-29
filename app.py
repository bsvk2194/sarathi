from asyncio import tasks
import shutil
from datetime import datetime
from flask import Flask, jsonify, request, render_template
import sqlite3
from datetime import datetime, timedelta
import calendar
import dateparser
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)

DATABASE = "sarathi.db"
LAST_TASK_RESULTS = []
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize database
def init_db():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def create_backup():

    backup_name = (
        "/storage/emulated/0/SARATHI_SYNC/"
        f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    )

    shutil.copy(
        "sarathi.db",
        backup_name
    )

    cleanup_backups()

def cleanup_backups():

    backup_folder = "/storage/emulated/0/SARATHI_SYNC"

    backups = []

    for file in os.listdir(backup_folder):

        if file.startswith("backup_") and file.endswith(".db"):

            full_path = os.path.join(
                backup_folder,
                file
            )

            backups.append(full_path)

    backups.sort(
        key=os.path.getmtime,
        reverse=True
    )

    for old_backup in backups[50:]:

        os.remove(old_backup)

# Home route
@app.route('/')
def home():

    return jsonify({
        "project": "SARATHI",
        "status": "online",
        "database": "connected"
    })

@app.route('/tasks-page')
def tasks_page():

    return render_template("tasks.html")

@app.route('/dashboard')
def dashboard():

    return render_template("home.html")

@app.route('/notes-page')
def notes_page():

    return render_template("notes.html")

@app.route('/calendar-page')
def calendar_page():

    return render_template("calendar.html")

# Health route
@app.route('/health')
def health():

    return jsonify({
        "server_status": "running",
        "database": "active",
        "network": "connected"
    })

# Storage route
@app.route('/storage')
def storage():
    return render_template('storage.html')

# Test intent route
@app.route("/test-intent", methods=["POST"])
def test_intent():

    data = request.get_json()

    message = data["message"]

    result = classify_intent(message)

    return jsonify({
        "result": result
    })

# Intent classification function
def classify_intent(user_message):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = """
You are the intent classifier for SARATHI.

Your ONLY job is to determine the user's intent.

DO NOT answer the user.

DO NOT explain anything.

Return ONLY valid JSON.

Always use this format:

{
    "intent": "...",
    "parameters": { ... }
}

Available intents:

--------------------------------------------------

1. add_task

When the user wants to remember or complete something.

Examples:

- I need to buy milk.
- Remind me to study.
- Add task finish project.

Return:

{
    "intent":"add_task",
    "parameters":{
        "task":"..."
    }
}

--------------------------------------------------

2. search_notes

When the user wants to search notes.

Examples:

- Show notes about Flask.
- Find my notes on Python.
- Search notes for SQL.

Return:

{
    "intent":"search_notes",
    "parameters":{
        "query":"..."
    }
}

--------------------------------------------------

3. pending_tasks

If the user asks for the NUMBER of pending tasks:

Examples:

- How many pending tasks?
- Pending task count.

Return:

{
    "intent":"pending_tasks",
    "parameters":{
        "mode":"count"
    }
}

If the user wants to SEE the pending tasks:

Examples:

- Show pending tasks.
- List my pending tasks.
- What tasks are left?

Return:

{
    "intent":"pending_tasks",
    "parameters":{
        "mode":"list"
    }
}

--------------------------------------------------

4. latest_note

Examples:

- What is my latest note?
- Show my most recent note.
- Show my newest note.
- What was the last note I saved?

Return:

{
    "intent":"latest_note",
    "parameters":{}
}

--------------------------------------------------

5. upcoming_events

Return:

{
    "intent":"upcoming_events",
    "parameters":{}
}

--------------------------------------------------

6. storage_status

Return:

{
    "intent":"storage_status",
    "parameters":{}
}

--------------------------------------------------

7. backup_count

Return:

{
    "intent":"backup_count",
    "parameters":{}
}

--------------------------------------------------

8. complete_task

When completing an existing task.

Examples:

- Complete task buy milk.
- Mark buy milk as done.
- Finish task buy milk.

Return:

{
    "intent":"complete_task",
    "parameters":{
        "task":"..."
    }
}

--------------------------------------------------

9. add_event

Examples:

- Add meeting tomorrow.
- Schedule dentist appointment.
- Create event birthday party.

Return:

{
    "intent":"add_event",
    "parameters":{
        "title":"...",
        "date":"..."
    }
}

--------------------------------------------------

10. general_chat

Use this only if none of the above intents apply.

Return:

{
    "intent":"general_chat",
    "parameters":{}
}

"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": prompt
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

    content = response.json()["choices"][0]["message"]["content"]

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return {
            "intent": "general_chat",
            "parameters": {}
        }

# AI assistant route
@app.route('/ask-ai', methods=['POST'])
def ask_ai():

    data = request.get_json()

    user_message = data.get("message", "")

    intent_data = classify_intent(user_message)

    intent = intent_data["intent"]

    parameters = intent_data["parameters"]

    message_lower = user_message.lower()

    global LAST_TASK_RESULTS
    
    if intent == "pending_tasks":

        mode = parameters.get("mode","")

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

            LAST_TASK_RESULTS = tasks

            conn.close()

            if not tasks:

                return jsonify({
                    "reply": "You have no pending tasks."
                })

            task_list = ""

            for i, task in enumerate(tasks, start=1):

                task_list += (
                    f"{i}. {task[1]}\n"
                )

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
        
        else:
            return jsonify({
                "reply": "I couldn't determine whether you wanted the task list or the task count."
            })
    
    elif intent == "latest_note":

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
    
    elif intent == "search_notes":

        keyword = parameters.get("query", "").strip()

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
    
    elif ("event" in message_lower and ("upcoming" in message_lower or "coming up" in message_lower)):

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
    
    elif intent == "storage_status":
        
        total, used, free = shutil.disk_usage(
            "/storage/emulated/0"
        )

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
    
    elif ("backup" in message_lower and ("count" in message_lower or "many" in message_lower or "how" in message_lower)):

        backup_folder = (
            "/storage/emulated/0/SARATHI_SYNC"
        )

        backup_count = len([
            f for f in os.listdir(
                backup_folder
            )
            if f.startswith("backup_")
            and f.endswith(".db")
        ])

        return jsonify({
            "reply":
            f"You currently have {backup_count} backups."
        })

    elif intent == "add_task":

        task_text = parameters.get("task", "").strip()

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
    
    elif ("add note" in message_lower or "add a note" in message_lower or "create note" in message_lower or "create a note" in message_lower):

        if "add note" in message_lower:

            note_text = user_message[len("add note"):].strip()

        elif "add a note" in message_lower:

            note_text = user_message[len("add a note"):].strip()

        elif "create note" in message_lower:

            note_text = user_message[len("create note"):].strip()

        else:

            note_text = user_message[len("create a note"):].strip()

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
    
    elif ("complete task" in message_lower or "finish task" in message_lower or "mark task" in message_lower 
          or "complete the task" in message_lower or "mark the task" in message_lower or "finish the task" in message_lower):

        if "complete task" in message_lower:

            task_name = user_message[len("complete task"):].strip()

        elif "mark task" in message_lower:

            task_name = user_message[len("mark task"):].strip()

        elif "finish task" in message_lower:

            task_name = user_message[len("finish task"):].strip()

        elif "complete the task" in message_lower:

            task_name = user_message[len("complete the task"):].strip()

        elif "mark the task" in message_lower:

            task_name = user_message[len("mark the task"):].strip()

        elif "finish the task" in message_lower:

            task_name = user_message[len("finish the task"):].strip()


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
    
    elif ("add event" in message_lower or "create event" in message_lower 
          or "add an event" in message_lower or "create an event" in message_lower):

        if "add event" in message_lower:

            event_text = user_message[len("add event"):].strip()

        elif "create event" in message_lower:

            event_text = user_message[len("create event"):].strip()

        elif "add an event" in message_lower:

            event_text = user_message[len("add an event"):].strip()

        elif "create an event" in message_lower:

            event_text = user_message[len("create an event"):].strip()


        parts = event_text.rsplit(" ", 1)

        if len(parts) < 2:

            return jsonify({
                "reply":
                "Use the format:\n\nAdd event <title> <date>"
            })

        title = parts[0]

        event_date = parts[1]

        parsed_date = dateparser.parse(
            event_date,
            settings={
                "PREFER_DATES_FROM": "future"
            }
        )

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
    
    elif ("complete the" in message_lower):

        if not LAST_TASK_RESULTS:

            return jsonify({
                "reply":
                "No recent task list found."
            })

        words = message_lower.split()

        if len(words) < 4:

            return jsonify({
                "reply":
                "Specify which task."
            })

        position_word = words[2]

        mapping = {
            "first":0,
            "second":1,
            "third":2,
            "fourth":3,
            "fifth":4
        }

        if position_word not in mapping:

            return jsonify({
                "reply":
                "Unknown task position."
            })

        index = mapping[position_word]

        if index >= len(LAST_TASK_RESULTS):

            return jsonify({
                "reply":
                "Task number out of range."
            })

        task_id =LAST_TASK_RESULTS[index][0]

        task_name =LAST_TASK_RESULTS[index][1]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET completed=1
            WHERE id=?
            """,
            (task_id,)
        )

        conn.commit()
        create_backup()
        conn.close()

        return jsonify({
            "reply":
            f"Completed task: {task_name}"
        })

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

    reply = response.json()["choices"][0]["message"]["content"]

    return jsonify({
        "reply": reply
    })

# Create Backup route
@app.route('/create-backup', methods=['POST'])
def create_backup_route():

    create_backup()

    return jsonify({
        "message": "Backup created successfully"
    })

# Backup history route
@app.route('/backup-history')
def backup_history():

    backup_folder = (
        "/storage/emulated/0/SARATHI_SYNC"
    )

    backups = []

    for file in sorted(
        os.listdir(backup_folder),
        reverse=True
    ):

        if (
            file.startswith("backup_")
            and file.endswith(".db")
        ):

            backups.append({
                "name": file
            })

    return jsonify(backups)

@app.route('/dashboard-data')
def dashboard_data():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    total_tasks = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE completed=1
        """
    )

    completed_tasks = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT title, event_date
        FROM events
        ORDER BY event_date ASC
        LIMIT 3
        """
    )

    upcoming_events = cursor.fetchall()

    cursor.execute(
        """
        SELECT content
        FROM notes
        ORDER BY created_at DESC
        LIMIT 1
        """
    )

    latest_note = cursor.fetchone()

    total, used, free = shutil.disk_usage(
    "/storage/emulated/0"
    )

    total_gb = round(total / (1024**3), 2)
    used_gb = round(used / (1024**3), 2)
    free_gb = round(free / (1024**3), 2)

    conn.close()

    backup_folder = "/storage/emulated/0/SARATHI_SYNC"

    backup_count = len([
        f for f in os.listdir(backup_folder)
        if f.startswith("backup_")
        and f.endswith(".db")
    ])

    backups = [
    f for f in os.listdir(backup_folder)
    if f.startswith("backup_")
    and f.endswith(".db")
    ]

    latest_backup = (
        max(backups)
        if backups
        else "No backups"
    )


    events = []

    for event in upcoming_events:

        events.append({
            "title": event[0],
            "date": event[1]
        })


    return jsonify({

        "total_tasks": total_tasks,

        "completed_tasks": completed_tasks,

        "pending_tasks":
            total_tasks - completed_tasks,

        "events": events,

        "latest_note":
            latest_note[0]
            if latest_note else "No notes yet",

        "storage": {

            "total_gb": total_gb,

            "used_gb": used_gb,

            "free_gb": free_gb

        },

        "backup_count": backup_count,

        "latest_backup": latest_backup

    })

# Get all notes
@app.route('/notes', methods=['GET'])
def get_notes():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes")
    rows = cursor.fetchall()

    conn.close()

    notes = []

    for row in rows:
        notes.append({
            "id": row[0],
            "content": row[1],
            "created_at": row[2]
        })

    return jsonify({
        "total_notes": len(notes),
        "notes": notes
    })


# Add note
@app.route('/notes', methods=['POST'])
def add_note():

    data = request.get_json()

    if not data or "note" not in data:

        return jsonify({
            "error": "No note provided"
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO notes (content) VALUES (?)",
        (data["note"],)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Note saved successfully"
    })

# Delete note
@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Note deleted"
    })

# Edit note
@app.route('/notes/<int:note_id>', methods=['PUT'])
def edit_note(note_id):

    data = request.get_json()

    if not data or "content" not in data:

        return jsonify({
            "error": "Content missing"
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE notes SET content = ? WHERE id = ?",
        (data["content"], note_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Note updated"
    })

# Get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    conn.close()

    tasks = []

    for row in rows:

        tasks.append({
            "id": row[0],
            "task": row[1],
            "completed": bool(row[2]),
            "created_at": row[3]
        })

    return jsonify({
        "total_tasks": len(tasks),
        "tasks": tasks
    })


# Add new task
@app.route('/tasks', methods=['POST'])
def add_task():

    data = request.get_json()

    if not data or "task" not in data:

        return jsonify({
            "error": "Task missing"
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (task) VALUES (?)",
        (data["task"],)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task created"
    })


# Toggle task completion
@app.route('/tasks/<int:task_id>/toggle', methods=['PUT'])
def toggle_task(task_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT completed FROM tasks WHERE id=?",
        (task_id,)
    )

    task = cursor.fetchone()

    if not task:

        conn.close()

        return jsonify({
            "error": "Task not found"
        }), 404

    new_status = 0 if task[0] else 1

    cursor.execute(
        "UPDATE tasks SET completed=? WHERE id=?",
        (new_status, task_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task updated",
        "completed": bool(new_status)
    })

# Edit task
@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def edit_task(task_id):

    data = request.get_json()

    if not data or "task" not in data:

        return jsonify({
            "error": "Task text missing"
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET task = ? WHERE id = ?",
        (data["task"], task_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task updated"
    })

# Delete task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task deleted"
    })

#get events
@app.route('/events', methods=['GET'])
def get_events():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM events
        ORDER BY event_date ASC
    """)

    rows = cursor.fetchall()

    conn.close()

    events = []

    for row in rows:

        events.append({
            "id": row[0],
            "title": row[1],
            "event_date": row[2],
            "created_at": row[3]
        })

    return jsonify({
        "events": events
    })

#add event
@app.route('/events', methods=['POST'])
def add_event():

    data = request.get_json()

    if not data:
        return jsonify({
            "error":"Missing data"
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO events
        (title, event_date)
        VALUES (?, ?)
        """,
        (
            data["title"],
            data["event_date"]
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message":"Event added"
    })

#delete event
@app.route('/events/<int:event_id>',methods=['DELETE'])
def delete_event(event_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM events WHERE id=?",
        (event_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message":"Event deleted"
    })


# Start server
if __name__ == '__main__':

    init_db()

    app.run(
        host='0.0.0.0',
        port=5000
    )