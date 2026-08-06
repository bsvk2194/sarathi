"""
LLM Service for SARATHI.

Contains domain-specific prompting and reasoning
built on top of the LLM provider framework.
"""


import json
from core.llms.loader import load_llms
from core.llms.manager import llms


load_llms()

def retrieve_memory_numbers(query, memories):

    memory_text = ""

    for i, memory in enumerate(memories, start=1):

        memory_text += f"{i}. {memory[1]}\n"

    prompt = f"""
    You are a semantic memory retrieval engine.

    Your ONLY job is to identify memories that could help answer the user's request.

    Include:
    - Directly relevant memories.
    - Closely related memories that provide useful context.

    Do not include unrelated memories.

    Return ONLY a valid JSON array of memory numbers.

    Example:

    [1,3]
    []
    [1]


    Do not explain.
    Do not use markdown.
    Do not write anything except the JSON array.

    User Query:

    {query}

    Stored Memories:

    {memory_text}
    """

    response = llms.groq.generate(
    system_prompt=prompt,
    user_prompt=query
)

    if not response.success:
        return []

    content = response.content

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return []
    
def find_similar_memories(new_memory, memories):

    memory_text = ""

    for i, memory in enumerate(memories, start=1):

        memory_text += f"{i}. {memory[1]}\n"

    prompt = f"""
    You are a semantic duplicate detection engine.

    Your task is to identify ONLY memories that express the exact same fact.

    A memory is a duplicate only if both memories communicate the same underlying fact.
    If both memories can coexist without contradiction or redundancy, they are NOT duplicates.

    Do NOT mark memories as duplicates simply because they mention the same person, project, object, or topic.

    Examples:

    Duplicate:
    New: SARATHI uses Python.
    Existing: SARATHI uses Python.

    Duplicate:
    New: My favorite language is Python.
    Existing: I like Python the most.

    NOT duplicates:
    New: SARATHI uses Python.
    Existing: SARATHI uses Flask.

    NOT duplicates:
    New: SARATHI uses SQLite.
    Existing: SARATHI uses Python.

    NOT duplicates:
    New: My favorite language is Python.
    Existing: I know Python.

    NOT duplicates:
    New: I live in Hyderabad.
    Existing: I work in Hyderabad.

    NOT duplicates:
    New: My laptop has 16 GB RAM.
    Existing: My laptop uses an Intel processor.

    Return ONLY a valid JSON array of duplicate memory numbers.

    If none are duplicates, return:

    []

    [2]

    [1,3]

    Do not explain your answer.
    Do not use markdown.
    Do not write anything except the JSON array.

    New Memory:

    {new_memory}

    Existing Memories:

    {memory_text}
    """

    response = llms.groq.generate(
    system_prompt=prompt,
    user_prompt=new_memory
)

    if not response.success:
        return []

    content = response.content

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return []
    
def reason_over_memories(question, memories):

    memory_text = ""

    for i, memory in enumerate(memories, start=1):

        memory_text += f"{i}. {memory[1]}\n"

    prompt = f"""
    You are SARATHI's knowledge reasoning engine.

    Your ONLY job is to answer the user's question using ONLY the provided memories.

    Rules:

    1. Use only the supplied memories.
    2. Never invent information.
    3. If the memories are insufficient, clearly say so.
    4. Combine related memories into a natural response.
    5. Do not mention memory numbers.
    6. Do not mention that you were given memories.
    7. Answer in plain English.

    Relevant Memories:

    {memory_text}
    """

    response = llms.groq.generate(
    system_prompt=prompt,
    user_prompt=question
)

    if not response.success:
        return "I couldn't reason about your memories right now."

    return response.content

    return content

def find_contradicting_memory_numbers(new_memory, memories):

    memory_text = ""

    for i, memory in enumerate(memories, start=1):

        memory_text += f"{i}. {memory[1]}\n"

    prompt = f"""
    You are a contradiction detection engine.

    Your ONLY job is to identify which memories contradict the new memory.

    Return ONLY a valid JSON array of memory numbers.

    Example:

    [1]
    [2,4]
    []

    Rules:

    - Return ONLY contradictions.
    - Do NOT return duplicates.
    - Do NOT return related memories.
    - Do NOT explain your reasoning.
    - Do NOT use markdown.
    - Do NOT write anything except the JSON array.

    New Memory:

    {new_memory}

    Existing Memories:

    {memory_text}
    """

    response = llms.groq.generate(
    system_prompt=prompt,
    user_prompt=new_memory
)

    if not response.success:
        return []

    content = response.content

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return []


def select_tool(user_request, available_tools):

    tool_text = ""

    for tool in available_tools:

        tool_text += f"- {tool}\n"

    prompt = f"""
    You are SARATHI's tool routing engine.

    Your ONLY job is to determine which tool should handle the user's request.

    Available Tools:

    {tool_text}

    Rules:

    - Return ONLY one tool name.
    - The tool name MUST exactly match one of the available tools.
    - If no tool is appropriate, return:

    none

    Do not explain.
    Do not use markdown.
    Do not write anything except the tool name.
    """

    response = llms.groq.generate(
    system_prompt=prompt,
    user_prompt=user_request
)

    if not response.success:
        return None

    content = response.content

    content = content.strip().lower()

    if content == "none":
        return None

    if content not in available_tools:
        return None

    return content