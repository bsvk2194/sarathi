import json
import os
import requests

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_llm(system_prompt, user_prompt="", temperature=0):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "temperature": temperature,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        response.raise_for_status()

    except requests.RequestException:
        return None

    content = response.json()["choices"][0]["message"]["content"]

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return content

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

    content = ask_llm(
        system_prompt=prompt,
        user_prompt=query
    )

    if content is None:
        return []

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

    content = ask_llm(
        system_prompt=prompt,
        user_prompt=new_memory
    )

    if content is None:
        return []

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

    content = ask_llm(
        system_prompt=prompt,
        user_prompt=question
    )

    if content is None:
        return "I couldn't reason about your memories right now."

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

    content = ask_llm(
        system_prompt=prompt,
        user_prompt=new_memory
    )

    if content is None:
        return []

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return []
