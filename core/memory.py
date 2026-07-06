from flask import jsonify

MEMORY = {

    "last_task_results": [],

    "last_note_results": [],

    "last_event_results": [],

    "last_intent": None,

    "last_parameters": {},

    "last_reply": None

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

def remember_reply(reply):
    set_memory("last_reply", reply)
    print(MEMORY)
    return jsonify({"reply": reply})
def print_memory():

    print(MEMORY)