import sqlite3
from flask import jsonify
from core.backup import create_backup
from core.memory import get_pending_action, remember_reply, resolve_recent_reference, resolve_reference, set_memory, get_memory, print_memory, set_conversation_state
from core.handlers import (
    handle_latest_note,
    handle_storage_status,
    handle_backup_count,
    handle_pending_tasks,
    handle_complete_task,
    handle_complete_task_by_id,
    handle_add_task,
    handle_search_notes,
    handle_add_note,
    handle_upcoming_events,
    handle_add_event,
    handle_create_backup,
    handle_general_chat
)
from core.handlers.knowledge import (
    handle_finish_memory_edit,
    handle_forget_memory,
    handle_remember,
    handle_list_memories,
    handle_retrieve_semantic_memories,
    handle_search_memories,
    handle_forget_memories,
    handle_update_memory,
    handle_edit_memory_reference    
)

DATABASE = "sarathi.db"

def dispatch_intent(intent_data, user_message):

    intent = intent_data["intent"]

    parameters = intent_data["parameters"]

    pending = get_pending_action()  

    if pending is not None and pending["type"] == "edit_memory":

        return handle_finish_memory_edit(

        pending["memory_id"],

        user_message
    )

    set_memory("last_intent", intent)
    set_memory("last_parameters", parameters)
    #print_memory()

    message_lower = user_message.lower()
    
    if intent == "pending_tasks":

        set_conversation_state(
            "tasks",
            "listing"
        )

        return handle_pending_tasks(
            parameters.get("mode", "")
        )
    
    elif intent == "latest_note":

        set_conversation_state(
            "notes",
            "viewing"
        )

        return handle_latest_note()
    
    elif intent == "search_notes":

        set_conversation_state(
        "notes",
        "searching"
    )

        return handle_search_notes(
        parameters.get("query", "")
    )
    
    elif intent == "upcoming_events":

        set_conversation_state(
            "events",
            "listing"
        )

        return handle_upcoming_events()
    
    elif intent == "storage_status":

        set_conversation_state(
        "system",
        "storage"
    )

        return handle_storage_status()
    
    elif intent == "backup_count":

        set_conversation_state(
        "system",
        "backup"
    )

        return handle_backup_count()

    elif intent == "add_task":

        set_conversation_state(
            "tasks",
            "creating"
        )

        return handle_add_task(
        parameters.get("task", "")
    )
    
    elif intent == "add_note":

        set_conversation_state(
        "notes",
        "creating"
    )

        return handle_add_note(
        parameters.get("note", "")
    )
    
    elif intent == "complete_task":

        task = parameters.get("task", "").strip()

        set_conversation_state(
            "tasks",
            "completing"
        )

        resolved = resolve_recent_reference(task) 

        if resolved:

            task_id = resolved[0]

            return handle_complete_task_by_id(task_id)

        return handle_complete_task(task)
    
    elif intent == "add_event":

        set_conversation_state(
            "events",
            "creating"
        )

        return handle_add_event(
        parameters.get("title", ""),
        parameters.get("date", "")
    )
    
    
    elif intent == "create_backup":

        set_conversation_state(
            "system",
            "backup"
        )

        return handle_create_backup()
    
    elif intent == "remember":

        set_conversation_state(
            "knowledge",
            "creating"
        )

        return handle_remember(
            parameters.get("content", ""),
            parameters.get("importance", 1)
        )
    
    elif intent == "list_memories":

        set_conversation_state(
            "knowledge",
            "listing"
        )

        return handle_list_memories()
    
    elif intent == "search_memories":

        set_conversation_state(
            "knowledge",
            "searching"
        )

        return handle_search_memories(
            parameters.get("query", "")
        )
    
    elif intent == "forget_memory":

            set_conversation_state(
                "knowledge",
                "deleting"
            )

            resolved = resolve_recent_reference(
                parameters.get("reference", "")
            )

            if resolved is None:

                return remember_reply(
                    "I couldn't determine which memory you meant."
                )

            return handle_forget_memory(
                resolved[0]
            )
    
    elif intent == "forget_memory_search":

        set_conversation_state(
            "knowledge",
            "deleting"
        )

        return handle_forget_memories(
            parameters.get("query", "")
        )
    
    elif intent == "update_memory":

        set_conversation_state(
            "knowledge",
            "editing"
        )

        return handle_update_memory(

            parameters.get("query", ""),

            parameters.get("replacement", "")
        )
    
    elif intent == "edit_memory_reference":

        set_conversation_state(
            "knowledge",
            "editing"
        )

        resolved = resolve_recent_reference(
            parameters.get("reference", "")
        )

        if resolved is None:

            return remember_reply(
                "I couldn't determine which memory you meant."
            )

        return handle_edit_memory_reference(
            resolved[0]
        )
    
    elif intent == "semantic_memory_search":

        set_conversation_state(
            "knowledge",
            "retrieving"
        )

        return handle_retrieve_semantic_memories(

            parameters.get("query", "")

        )
    
    set_conversation_state(
        "chat",
        "conversation"
    )

    return handle_general_chat(user_message)


    
