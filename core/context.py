
from core.knowledge import retrieve_semantic_memories
from core.understanding import build_user_model
from core.user_model import build_dynamic_model
from core.knowledge_service import get_knowledge

def get_context(user_message):

    return get_knowledge(user_message)


def build_prompt(context, user_message):

    knowledge_graph = context["knowledge_graph"]
    dynamic_model = context["dynamic_model"]
    prompt_context = context["prompt_context"]

    prompt = ""

    sections = [
        ("Projects", "projects"),
        ("Skills", "skills"),
        ("Technologies", "technologies"),
        ("Preferences", "preferences"),
        ("Goals", "goals")
    ]

    has_context = any(prompt_context.get(key) for _, key in sections)

    if has_context:

        prompt += "=== Relevant User Context ===\n\n"

        for title, key in sections:

            if prompt_context.get(key):

                prompt += f"=== {title} ===\n\n"

                for item in prompt_context.get(key):
                    prompt += f"- {item}\n"

                prompt += "\n"

        prompt += (
            "=== Instructions ===\n\n"
            "- Use the context only if it genuinely helps answer the user's request.\n"
            "- Do not force references to the context.\n"
            "- If the context is unrelated, ignore it completely.\n"
            "- Do not mention that you were given context unless it naturally fits the conversation.\n"
            "- Respond naturally, as if you already know the user.\n\n"
        )

    prompt += "=== User Request ===\n\n"
    prompt += user_message

    return prompt   



    