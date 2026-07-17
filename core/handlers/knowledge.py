from flask import jsonify

from core.knowledge import (
    remember,
    get_all_memories,
    retrieve_semantic_memories,
    search_memories,
    forget_memory,
    forget_memories,
    update_memory,
    update_memory_by_id,
    find_duplicate_memories,
    answer_from_memories
)

from core.memory import (get_recent_results,remember_reply, set_pending_action,set_recent_results,
    clear_pending_action,resolve_recent_reference)


def handle_remember(content, importance = 1):

    content = content.strip()


    if content == "":

        reply = "Please tell me what you want me to remember."

        return remember_reply(reply)
    
    duplicates = find_duplicate_memories(content)

    if duplicates:

        duplicate_list = ""

        for duplicate in duplicates:

            duplicate_list += f"• {duplicate[1]}\n"

        reply = f"""I already have similar memory(s):

    {duplicate_list}

    I haven't saved this memory to avoid creating duplicates.
    """

        return remember_reply(reply)
    
    remember(
        content,
        importance
    )

    remember(content, importance)

    reply = f"I'll remember:\n\n{content}"

    return remember_reply(reply)

def handle_list_memories():

    memories = get_all_memories()
    set_recent_results(
        "knowledge",
        memories
    )
    #print(get_recent_results())

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
    set_recent_results(
        "knowledge",
        memories
    )
    #print(get_recent_results())

    if not memories:

        reply = "No matching memories found."

        return remember_reply(reply)

    memory_list = ""

    for i, memory in enumerate(memories, start=1):

        memory_list += f"{i}. {memory[1]}\n"

    reply = f"Found {len(memories)} matching memories.\n\n{memory_list}"

    return remember_reply(reply)

def handle_forget_memory(memory_id):

    forgotten = forget_memory(memory_id)

    if forgotten is None:

        reply = "I couldn't find that memory."

        return remember_reply(reply)

    reply = f"""Forgot:

    {forgotten}
    """

    return remember_reply(reply)

def handle_forget_memories(query):

    query = query.strip()

    if query == "":

        reply = "Please tell me what memories to forget."

        return remember_reply(reply)

    memories = forget_memories(query)

    if not memories:

        reply = f"No memories found about '{query}'."

        return remember_reply(reply)

    memory_list = ""

    for memory in memories:

        memory_list += f"• {memory[1]}\n"

    reply = f"""Forgot {len(memories)} memory(s).

{memory_list}
"""

    return remember_reply(reply)

def handle_update_memory(query, replacement):

    result = update_memory(
        query,
        replacement
    )

    if result is None:

        reply = "I couldn't find a matching memory."

        return remember_reply(reply)

    old_memory, new_memory = result

    reply = f"""Updated memory.

Before:
{old_memory}

After:
{new_memory}
"""

    return remember_reply(reply)

def handle_edit_memory_reference(memory_id):

    set_pending_action({

        "type": "edit_memory",

        "memory_id": memory_id

    })

    reply = "What would you like me to change it to?"

    return remember_reply(reply)

def handle_finish_memory_edit(memory_id, new_content):

    result = update_memory_by_id(
        memory_id,
        new_content
    )

    if result is None:

        clear_pending_action()

        reply = "I couldn't find that memory."

        return remember_reply(reply)

    clear_pending_action()

    old_memory, updated_memory = result

    reply = f"""Updated memory.

Before:
{old_memory}

After:
{updated_memory}
"""

    return remember_reply(reply)

def handle_retrieve_semantic_memories(query):

    result = answer_from_memories(query)

    if result is None:

        reply = "I couldn't find any relevant memories."

        return remember_reply(reply)

    answer, memories = result

    set_recent_results(
        "knowledge",
        memories
    )

    return remember_reply(answer)