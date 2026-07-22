import json
import os
from wsgiref import headers
import requests

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def retrieve_memory_numbers(query, memories):

    memory_text = ""

    for i, memory in enumerate(memories, start=1):

        memory_text += f"{i}. {memory[1]}\n"

    prompt = f"""
    You are a semantic memory retrieval engine.

    Your ONLY job is to identify which memories are relevant.

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

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": query 
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:

        return []
    
    content = response.json()["choices"][0]["message"]["content"]

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

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

    Your ONLY job is to determine whether the new memory is the same as,
    or expresses substantially the same information as,
    one or more existing memories.

    Return ONLY a valid JSON array containing the matching memory numbers.

    Examples:

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

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": new_memory
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:

        return []
    
    content = response.json()["choices"][0]["message"]["content"]

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

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

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {

        "model": "llama-3.3-70b-versatile",

        "temperature": 0,

        "messages": [

            {

                "role": "system",

                "content": prompt

            },

            {

                "role": "user",

                "content": question

            }

        ]

    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:

        return "I couldn't reason about your memories right now."
    
    content = response.json()["choices"][0]["message"]["content"]

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return content.strip()

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

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": new_memory
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:

        return []

    content = response.json()["choices"][0]["message"]["content"]

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return []
