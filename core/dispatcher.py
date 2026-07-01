import sqlite3
from flask import jsonify
from core.backup import create_backup
from core.memory import LAST_TASK_RESULTS
from core.handler import (
    handle_latest_note,
    handle_storage_status,
    handle_backup_count,
    handle_pending_tasks,
    handle_complete_task,
    handle_add_task,
    handle_search_notes,
    handle_add_note,
    handle_upcoming_events,
    handle_add_event,
    handle_general_chat,
    handle_create_backup
)

DATABASE = "sarathi.db"

def dispatch_intent(intent_data, user_message):

    intent = intent_data["intent"]

    parameters = intent_data["parameters"]

    message_lower = user_message.lower()

    global LAST_TASK_RESULTS
    
    if intent == "pending_tasks":

        return handle_pending_tasks(
        parameters.get("mode", "")
    )
    
    elif intent == "latest_note":

        return handle_latest_note()
    
    elif intent == "search_notes":

        return handle_search_notes(
        parameters.get("query", "")
    )
    
    elif intent == "upcoming_events":

        return handle_upcoming_events()
    
    elif intent == "storage_status":

        return handle_storage_status()
    
    elif intent == "backup_count":

        return handle_backup_count()

    elif intent == "add_task":

        return handle_add_task(
        parameters.get("task", "")
    )
    
    elif intent == "add_note":

        return handle_add_note(
        parameters.get("note", "")
    )
    
    elif intent == "complete_task":

         return handle_complete_task(
        parameters.get("task", "")
    )
    
    elif intent == "add_event":

        return handle_add_event(
        parameters.get("title", ""),
        parameters.get("date", "")
    )
    
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
    
    elif intent == "create_backup":

        return handle_create_backup()

    return handle_general_chat(user_message)
