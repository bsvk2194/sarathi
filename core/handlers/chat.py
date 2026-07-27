import os
import requests

from dotenv import load_dotenv
from flask import jsonify
from core.memory import remember_reply  
from core.context import get_context, build_prompt
from core.memory_policy import should_use_context

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# General chat handler
def handle_general_chat(user_message):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    #print(f"Use Context: {should_use_context(user_message)}")
    
    if should_use_context(user_message):

        context = get_context(user_message)

        prompt = build_prompt(
            context,
            user_message
        )

    else:

        prompt = user_message

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are SARATHI, Karthik's personal AI operating system. "
                    "Be concise, practical and helpful."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:

        return remember_reply("I'm having trouble connecting to the language model right now.")


    reply = response.json()["choices"][0]["message"]["content"]

    return remember_reply(reply)