from flask import jsonify

from core.knowledge import (
    remember,
    get_all_memories,
    search_memories,
    forget_memory
)

from core.memory import remember_reply

def handle_remember(content):

    content = content.strip()

    if content == "":

        reply = "Please tell me what you want me to remember."

        return remember_reply(reply)

    remember(content)

    reply = f"I'll remember:\n\n{content}"

    return remember_reply(reply)

def handle_list_memories():

    memories = get_all_memories()

    if not memories:

        reply = "I don't have any saved memories yet."

        return remember_reply(reply)

    memory_list = ""

    for i, memory in enumerate(memories, start=1):

        memory_list += f"{i}. {memory[1]}\n"

    reply = f"Saved Memories:\n\n{memory_list}"

    return remember_reply(reply)

def handle_search_memories(query):

    query = query.strip()

    if query == "":

        reply = "Please tell me what to search for."

        return remember_reply(reply)

    memories = search_memories(query)

    if not memories:

        reply = "No matching memories found."

        return remember_reply(reply)

    memory_list = ""

    for i, memory in enumerate(memories, start=1):

        memory_list += f"{i}. {memory[1]}\n"

    reply = f"Found {len(memories)} matching memories.\n\n{memory_list}"

    return remember_reply(reply)