import shutil
import sqlite3
import os
from core.llm import reason_over_memories
from flask import Flask, jsonify, request, render_template
from core.classifier import classify_intent
from core.handlers import (handle_latest_note, handle_storage_status, handle_backup_count,
    handle_pending_tasks, handle_complete_task, handle_add_task,
    handle_search_notes, handle_add_note,
    handle_upcoming_events, handle_add_event,
    handle_create_backup, handle_general_chat)
from core.backup import (create_backup, cleanup_backups)
from core.dispatcher import dispatch_intent


app = Flask(__name__)

DATABASE = "sarathi.db"
LAST_TASK_RESULTS = []

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

    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS memories (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        content TEXT NOT NULL,

        importance INTEGER DEFAULT 1,

        usage_count INTEGER DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """
)

    conn.commit()
    conn.close()

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

# AI assistant route
@app.route('/ask-ai', methods=['POST'])
def ask_ai():

    data = request.get_json()

    user_message = data.get("message", "")

    intent_data = classify_intent(user_message)
    print(intent_data)

    return dispatch_intent(
        intent_data,
        user_message
    )

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

    if os.name == "nt":
        backup_folder = os.path.join(os.getcwd(), "backups")
    else:
        backup_folder = "/storage/emulated/0/SARATHI_SYNC"

    backups = []

    if not os.path.exists(backup_folder):
        return jsonify([])

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

    total, used, free = shutil.disk_usage(os.getcwd())

    total_gb = round(total / (1024**3), 2)
    used_gb = round(used / (1024**3), 2)
    free_gb = round(free / (1024**3), 2)

    conn.close()

    if os.name == "nt":
        backup_folder = os.path.join(os.getcwd(), "backups")
    else:
        backup_folder = "/storage/emulated/0/SARATHI_SYNC"

    if os.path.exists(backup_folder):

        backups = [
            f for f in os.listdir(backup_folder)
            if f.startswith("backup_")
            and f.endswith(".db")
        ]

    else:

        backups = []

    backup_count = len(backups)

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