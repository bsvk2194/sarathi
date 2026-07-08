import json
import os
import requests

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def classify_intent(user_message):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = """
You are the intent classifier for SARATHI.

Your ONLY job is to determine the user's intent.

DO NOT answer the user.

DO NOT explain anything.

Return ONLY valid JSON.

STRICT RULES

1. Return ONLY valid JSON.

2. Never include markdown.

3. Never include ```json or ```.

4. Never explain your answer.

5. Always return exactly two top-level keys:

{
    "intent": "...",
    "parameters": {}
}

6. Never omit the parameters object.

7. Never invent parameter names.

Use ONLY the parameter names defined below.

Always use this format:

{
    "intent": "...",
    "parameters": { ... }
}

Available intents:

--------------------------------------------------

1. add_task

When the user wants to remember or complete something.

Examples:

- I need to buy milk.
- Remind me to study.
- Add task finish project.

Return:

{
    "intent":"add_task",
    "parameters":{
        "task":"..."
    }
}

--------------------------------------------------

2. search_notes

When the user wants to search notes.

Examples:

- Show notes about Flask.
- Find my notes on Python.
- Search notes for SQL.

Return:

{
    "intent":"search_notes",
    "parameters":{
        "query":"..."
    }
}

--------------------------------------------------

3. pending_tasks

If the user asks for the NUMBER of pending tasks:

Examples:

- How many pending tasks?
- Pending task count.

Return:

{
    "intent":"pending_tasks",
    "parameters":{
        "mode":"count"
    }
}

If the user wants to SEE the pending tasks:

Examples:

- Show pending tasks.
- List my pending tasks.
- What tasks are left?

Return:

{
    "intent":"pending_tasks",
    "parameters":{
        "mode":"list"
    }
}

--------------------------------------------------

4. latest_note

Examples:

- What is my latest note?
- Show my most recent note.
- Show my newest note.
- What was the last note I saved?

Return:

{
    "intent":"latest_note",
    "parameters":{}
}

--------------------------------------------------

5. upcoming_events

Return:

{
    "intent":"upcoming_events",
    "parameters":{}
}

--------------------------------------------------

6. storage_status

Return:

{
    "intent":"storage_status",
    "parameters":{}
}

--------------------------------------------------

7. backup_count

Return:

{
    "intent":"backup_count",
    "parameters":{}
}

--------------------------------------------------

8. complete_task

When completing an existing task.

Examples:

- Complete task buy milk.
- Mark buy milk as done.
- Finish task buy milk.
- Complete the first one.
- Complete the second one.
- Complete the third one.
- Complete the last one.
- Complete the first task.
- Mark the second one as done.
- Finish the third task.

Never classify commands beginning with:

Complete
Finish
Mark

as add_task.

They always refer to complete_task.

If the user refers to a task by position
(first, second, third, fourth, fifth, last),

the intent MUST be:

{
    "intent":"complete_task",
    "parameters":{
        "task":"first one"
    }
}

else: 

Return:

{
    "intent":"complete_task",
    "parameters":{
        "task":"..."
    }
}

--------------------------------------------------

9. add_event

Examples:

- Add meeting tomorrow.
- Schedule dentist appointment.
- Create event birthday party.

Return:

{
    "intent":"add_event",
    "parameters":{
        "title":"...",
        "date":"..."
    }
}

--------------------------------------------------

10. Intent: add_note

Use when the user wants to save information as a note.

Examples:

- Add note buy Raspberry Pi.
- Save a note about Flask.
- Create a note saying Jai Shree Ram.

Return:

{
    "intent":"add_note",
    "parameters":{
        "note":"..."
    }
}

--------------------------------------------------

11. create_backup

When the user wants to manually create a backup.

Examples:

- Create a backup.
- Backup my data.
- Take a backup.
- Create database backup.
- Backup SARATHI.

Return:

{
    "intent":"create_backup",
    "parameters":{}
}

--------------------------------------------------

12. remember

Use when the user wants SARATHI to permanently remember something about them.

Examples:

- Remember that I use VS Code.
- Remember my birthday is July 15.
- Remember I prefer Python.
- Save this about me: I work night shifts.
- Keep this in mind: I use Arch Linux.
- Don't forget that I like Flask.
- Save this for later: I use VS Code.
- Keep this in mind: I prefer Flask.
- Don't forget that my favorite color is blue.

Return:

{
    "intent":"remember",
    "parameters":{
        "content":"..."
    }
}

--------------------------------------------------  

13. list_memories

Use when the user wants to see everything SARATHI remembers.

Examples:

- Show my memories.
- List my memories.
- What do you remember about me?
- What do you know about me?
- Tell me everything you remember.

Return:

{
    "intent":"list_memories",
    "parameters":{}
}

--------------------------------------------------

14. search_memories

Use when the user wants to search their saved memories.

Examples:

- Search memories for Python.
- Find memories about Flask.
- What do you remember about Linux?
- Search what you know about VS Code.

Return:

{
    "intent":"search_memories",
    "parameters":{
        "query":"..."
    }
}

--------------------------------------------------

If the user explicitly asks what SARATHI remembers about them, 
or asks to list or search saved memories,
never classify the request as general_chat.

--------------------------------------------------

15. general_chat

Use this only if none of the above intents apply.

Return:

{
    "intent":"general_chat",
    "parameters":{}
}

"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return {
            "intent": "general_chat",
            "parameters": {}
        }
    
    content = response.json()["choices"][0]["message"]["content"]

    '''print("=" * 60)
    print("CLASSIFIER RESPONSE")
    print("Status:", response.status_code)
    print(response.text)
    print("=" * 60)'''

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return {
            "intent": "general_chat",
            "parameters": {}
        }