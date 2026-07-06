import os
import shutil
import sqlite3

from core.memory import remember_reply
from core.config import DATABASE

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

        reply = "You do not have any notes yet."

        return remember_reply(reply)

    reply = f"Latest Note:\n\n{note[0]}"

    return remember_reply(reply)

# storage status handler
def handle_storage_status():

    total, used, free = shutil.disk_usage(os.getcwd())

    used_gb = round(
        used / (1024**3), 2
    )

    free_gb = round(
        free / (1024**3), 2
    )

    reply = f"""
    Storage Status

    Used: {used_gb} GB
    Free: {free_gb} GB
    """
    return remember_reply(reply)

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

    reply = f"You currently have {backup_count} backups."

    return remember_reply(reply)