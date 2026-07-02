import sqlite3
from flask import jsonify
from core.backup import create_backup
from core.memory import LAST_TASK_RESULTS
from core.handlers import (
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
    handle_create_backup,
    handle_general_chat
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
    
    
    elif intent == "create_backup":

        return handle_create_backup()

    return handle_general_chat(user_message)

''' To do  (Memory Manager):
    # Support follow-up commands like:
    # "complete the first one"
    # "delete the second note"
    # "move it to tomorrow" '''
    
