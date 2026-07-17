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

Use when the user wants SARATHI to permanently remember something.

Importance levels:

1 = Normal memory (default)
Examples:
- Remember that I use Python.
- Remember I use VS Code.
- Remember my birthday is July 15.

2 = Important memory
Examples:
- Remember this, it's important.
- This is important to remember.
- Please remember this, it's important.

3 = Critical memory
Examples:
- Never forget this.
- This is extremely important.
- This is critical.
- This is very important.

Return:

{
    "intent":"remember",
    "parameters":{
        "content":"...",
        "importance":1
    }
}

The importance value MUST be:

- 1 for normal memories (default)
- 2 for important memories
- 3 for critical / never forget memories

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

15. forget_memory   

Use when the user wants to delete a specific memory.

Examples:

- Forget the first one.
- Forget the second memory.
- Delete the third memory.
- Remove the first one I told you.

Return: 

{
    "intent":"forget_memory",
    "parameters":{
        "reference":"first"
    }
}

--------------------------------------------------

16. forget_memories

Use when the user wants to delete all memories.

Examples:

- Forget everything about Python.
- Forget anything related to Flask.
- Delete memories about Linux.
- Forget all memories about SQL.
- Remove everything you know about Arduino.

Return: 

{
    "intent":"forget_memory_search",
    "parameters":{
        "query":"Python"
    }
}

---------------------------------------------------

17. update_memory   

Use when the user wants to update a specific memory.

Examples:

- Replace VS Code with Cursor.
- Change Python to Rust.
- Update Flask to FastAPI.
- Replace Hyderabad with Bengaluru.

Return:

{
    "intent":"update_memory",
    "parameters":{

        "query":"VS Code",

        "replacement":"Cursor"

    }
}

---------------------------------------------------

18. edit_memory_reference

Use when the user wants to edit a specific memory by its ID.

Examples:

- Edit the first one.
- Edit the second memory.
- Modify the third memory.
- Change the first memory.
- Change the second one.

Return:

{
    "intent":"edit_memory_reference",
    "parameters":{
        "reference":"second"
    }
}

----------------------------------------------------

19. semantic_memory_search

Use when the user wants to search for relevant memories based on a query.

Examples:

- What programming languages do I use?
- What technologies do I use?
- What IDE do I use?
- What do you know about my projects?
- What software do I use?
- What frameworks do I use?

Return:

{
    "intent":"semantic_memory_search",
    "parameters":{
        "query":"What technologies do I use?"
    }
}

---------------------------------------------------

If the user explicitly asks what SARATHI remembers about them, 
or asks to list or search saved memories,
never classify the request as general_chat.

---------------------------------------------------

20. general_chat

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