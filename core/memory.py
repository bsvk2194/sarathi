from flask import jsonify

MEMORY = {

    "last_task_results": [],

    "last_note_results": [],

    "last_event_results": [],

    "last_intent": None,

    "last_parameters": {},

    "last_reply": None,

    "conversation_state": {

    "domain": None,

    "action": None

    }

}

ORDINAL_MAP = {

    "first": 0,
    "second": 1,
    "third": 2,
    "fourth": 3,
    "fifth": 4,

    "last": -1

}

def set_memory(key, value):

    MEMORY[key] = value


def get_memory(key):

    return MEMORY.get(key)


def clear_memory():

    MEMORY.clear()

    MEMORY.update({

        "last_task_results": [],

        "last_note_results": [],

        "last_event_results": [],

        "last_intent": None,

        "last_parameters": {},

        "last_reply": None

    })

def set_conversation_state(domain, action):

    MEMORY["conversation_state"] = {

        "domain": domain,

        "action": action

    }
    #print_conversation_state()  

def get_conversation_state():

    return MEMORY["conversation_state"]

# Future use:
#
# resolve_reference("first one", "last_task_results")
# resolve_reference("second note", "last_note_results")
# resolve_reference("third event", "last_event_results")
# resolve_reference("last reminder", "last_reminder_results")
#
# This resolver is intentionally generic so it can be reused
# across all SARATHI modules.

def resolve_reference(reference, memory_key):

    items = get_memory(memory_key)

    if not items:
        return None

    reference = reference.lower().strip()

    for word, index in ORDINAL_MAP.items():

        if word in reference:

            if index == -1:
                return items[-1]

            if index < len(items):
                return items[index]

            return None
        
    return None

def remember_reply(reply):
    set_memory("last_reply", reply)
    #print(MEMORY)
    return jsonify({"reply": reply})

def print_conversation_state():

    print(MEMORY["conversation_state"])

def print_memory():

    print(MEMORY)