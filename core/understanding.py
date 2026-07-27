import json

from core.llm import ask_llm


def build_user_model(memories):
    """
    Classifies retrieved memories into a structured user model.
    """

    if not memories:
        return {
            "projects": [],
            "skills": [],
            "technologies": [],
            "preferences": [],
            "goals": [],
            "unknown": []
        }

    prompt = build_understanding_prompt(memories)

    response = ask_llm(prompt)

    try:
        return json.loads(response)

    except json.JSONDecodeError:

        return {
            "projects": [],
            "skills": [],
            "technologies": [],
            "preferences": [],
            "goals": [],
            "relationships": [],
            "unknown": memories
        }


def build_understanding_prompt(memories):

    prompt = """
You are SARATHI's Understanding Engine.

Your job is to classify user memories into semantic categories.

Return ONLY valid JSON.

Schema:

{
    "projects": [],
    "skills": [],
    "technologies": [],
    "preferences": [],
    "goals": [],
    "relationships": [],
    "unknown": []
}

Rules:

- A project is something the user is building or working on.
- Skills are abilities or languages the user possesses.
- Technologies are frameworks, libraries, tools, or software.
- Preferences are personal likes or dislikes.
- Goals are long-term objectives.
- If unsure, place the item in "unknown".

Relationships describe how entities connect.

Use this schema:

{
    "source": "...",
    "relation": "...",
    "target": "..."
}

Example:

{
    "source":"SARATHI",
    "relation":"uses",
    "target":"Python"
}

Create relationships whenever they are clearly supported by the memories.

Do not invent relationships.
"""

    prompt += "\n\nMemories:\n\n"

    for memory in memories:
        prompt += f"- {memory}\n"

    prompt += "\nReturn only JSON."

    return prompt