import os
import shutil

from datetime import datetime

DATABASE = "sarathi.db"

def create_backup():

    if os.name == "nt":
        backup_folder = os.path.join(os.getcwd(), "backups")
    else:
        backup_folder = "/storage/emulated/0/SARATHI_SYNC"

    os.makedirs(backup_folder, exist_ok=True)

    backup_name = os.path.join(
        backup_folder,
        f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    )

    shutil.copy(
        DATABASE,
        backup_name
    )

    cleanup_backups()

def cleanup_backups():

    if os.name == "nt":
        backup_folder = os.path.join(os.getcwd(), "backups")
    else:
        backup_folder = "/storage/emulated/0/SARATHI_SYNC"

    if not os.path.exists(backup_folder):
        return

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