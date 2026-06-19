from asyncio import tasks
import shutil
from datetime import datetime
from flask import Flask, jsonify, request, render_template
import sqlite3
from datetime import datetime, timedelta
import calendar
import dateparser
import os

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

#assistant command route
@app.route('/assistant-command', methods=['POST'])
def assistant_command():

    data = request.get_json()

    command = data.get("command","").lower().strip()

    global LAST_TASK_RESULTS

    if command.startswith("add task"):

        task_text = command.replace(
            "add task",
            ""
        ).strip()

        if task_text == "":

            return jsonify({
                "response":
                "Please provide a task."
            })

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tasks
            (task, completed)
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
            WHERE completed=0
            """
        )

        pending_tasks = cursor.fetchone()[0]
        conn.close()

        return jsonify({
            "response":
            f"""
        Added task:
        {task_text}

        Pending tasks:
        {pending_tasks}
        """
        })
    if command.startswith("add event"):

        event_text = command.replace(
            "add event",
            ""
        ).strip()

        parts = event_text.rsplit(" ", 1)

        if len(parts) < 2:

            return jsonify({
                "response":
                "Use format: add event title YYYY-MM-DD"
            })

        title = parts[0]
        event_date = parts[1]

        parsed_date =dateparser.parse(event_date,settings={'PREFER_DATES_FROM': 'future'})

        if parsed_date:
            event_date =parsed_date.strftime("%Y-%m-%d")

        else:

            return jsonify({
                "response":
                "Could not understand the date."
            })

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
            "response":
            f"Event added: {title}"
        })
    
    if command.startswith("complete task"):

        task_name = command.replace(
            "complete task",
            ""
        ).strip()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM tasks
            WHERE LOWER(task)
            LIKE ?
            """,
            (f"%{task_name.lower()}%",)
        )

        task = cursor.fetchone()

        if not task:

            conn.close()

            return jsonify({
                "response":
                "Task not found."
            })

        cursor.execute(
            """
            UPDATE tasks
            SET completed=1
            WHERE id=?
            """,
            (task[0],)
        )

        conn.commit()
        create_backup()
        conn.close()

        return jsonify({
            "response":
            f"Task completed: {task_name}"
        })
    
    if command.startswith("add note"):

            note_text = command.replace(
                "add note",
                ""
            ).strip()

            if note_text == "":

                return jsonify({
                    "response":
                    "Please provide a note."
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
                "response":
                f"""
        Note saved:
        {note_text}

        Total notes:
        {total_notes}
        """
            })
    
    if command == "show pending tasks":

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, task
            FROM tasks
            WHERE completed=0
            """
        )

        tasks = cursor.fetchall()

        conn.close()

        if not tasks:

            return jsonify({
                "response":
                "No pending tasks."
            })
        

        LAST_TASK_RESULTS = tasks

        task_list = ""

        for i, task in enumerate(tasks, start=1):

            task_list += (
                f"{i}. {task[1]}\n"
            )

        return jsonify({
            "response":
            f"Pending Tasks:\n\n{task_list}"
        })
    
    if command == "show notes":

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT content
            FROM notes
            ORDER BY created_at DESC
            LIMIT 5
            """
        )

        notes = cursor.fetchall()

        conn.close()

        if not notes:

            return jsonify({
                "response":
                "No notes found."
            })

        notes_list = ""

        for i, note in enumerate(notes, start=1):

            notes_list += (
                f"{i}. {note[0]}\n"
            )

        return jsonify({
            "response":
            f"Recent Notes:\n\n{notes_list}"
        })
    
    if command.startswith("complete the"):

        if not LAST_TASK_RESULTS:

            return jsonify({
                "response":
                "No recent task list found."
            })

        words = command.split()

        if len(words) < 3:

            return jsonify({
                "response":
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
                "response":
                "Unknown task position."
            })

        index = mapping[position_word]

        if index >= len(LAST_TASK_RESULTS):

            return jsonify({
                "response":
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
            "response":
            f"Completed task: {task_name}"
        })

    if "hello" in command:

        return jsonify({
            "response":
            "Hello Karthik. SARATHI online."
        })

    if "status" in command:

        return jsonify({
            "response":
            "All systems operational."
        })

    return jsonify({
        "response":
        "Command not recognized yet."
    })

# Start server
if __name__ == '__main__':

    init_db()

    app.run(
        host='0.0.0.0',
        port=5000
    )