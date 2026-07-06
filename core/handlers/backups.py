from core.memory import remember_reply
from core.backup import create_backup

# backup creation handler
def handle_create_backup():

    create_backup()

    reply = "Backup created successfully."
    return remember_reply(reply)