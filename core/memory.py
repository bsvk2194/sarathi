from flask import jsonify

MEMORY = {

    "last_note_results": [],

    "last_event_results": [],

    "last_intent": None,

    "last_parameters": {},

    "last_reply": None,

    "conversation_state": {

    "domain": None,

    "action": None

    },
    "recent_results": {

    "domain": None,

    "results": []

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

def set_recent_results(domain, results):

    MEMORY["recent_results"] = {

        "domain": domain,

        "results": results

    }
    #print_recent_results()

def get_conversation_state():

    return MEMORY["conversation_state"]

def get_recent_results():

    return MEMORY["recent_results"]

# Future use:
#
# resolve_reference("first one", "last_task_results")
# resolve_reference("second note", "last_note_results")
# resolve_reference("third event", "last_event_results")
# resolve_reference("last reminder", "last_reminder_results")
#
# This resolver is intentionally generic so it can be reused
# across all SARATHI modules.

def resolve_reference(reference, items):

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

def resolve_recent_reference(reference):

    recent = get_recent_results()

    return resolve_reference(
        reference,
        recent["results"]
    )

def remember_reply(reply):
    set_memory("last_reply", reply)
    #print(MEMORY)
    return jsonify({"reply": reply})

def print_conversation_state():

    print(MEMORY["conversation_state"])

def print_recent_results():

    print(MEMORY["recent_results"])

def print_memory():

    print(MEMORY)