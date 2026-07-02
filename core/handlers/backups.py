from flask import jsonify

from core.backup import create_backup

# backup creation handler
def handle_create_backup():

    create_backup()

    return jsonify({
        "reply": "Backup created successfully."
    })