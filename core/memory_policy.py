import re

def should_use_context(user_message):

    words = re.findall(r"\b\w+\b", user_message.lower())

    print("WORDS:", words)

    context_keywords = {
        "i",
        "me",
        "my",
        "mine",
        "myself",
        "remember",
        "know",
        "preference",
        "prefer",
        "project",
        "projects",
        "technology",
        "technologies",
        "backend",
        "frontend",
        "framework",
        "use",
        "using",
        "continue",
        "sarathi"
    }

    for word in words:
        if word in context_keywords:
            print("MATCH:", word)
            return True

    return False

def build_prompt_context(knowledge, user_message):

    prompt_context = {

        "projects": [],
        "skills": [],
        "technologies": [],
        "goals": [],
        "preferences": []

    }

    graph = knowledge["knowledge_graph"]

    query = user_message.lower()

    dynamic_model = knowledge["dynamic_model"]

    current_project = dynamic_model.get("current_project")

    for project in graph["projects"]:

        if project.lower() in query:

            prompt_context["projects"].append(project)

    for tech in graph["technologies"]:

        if tech.lower() in query:

            prompt_context["technologies"].append(tech)

    for skill in graph["skills"]:

        if skill.lower() in query:

            prompt_context["skills"].append(skill)

    prompt_context["goals"] = graph["goals"]

    if current_project:

        if current_project not in prompt_context["projects"]:
            prompt_context["projects"].append(current_project)

    for technology in dynamic_model.get("current_technologies", []):

        if technology not in prompt_context["technologies"]:
            prompt_context["technologies"].append(technology)

    for skill in dynamic_model.get("current_skills", []):

        if skill not in prompt_context["skills"]:
            prompt_context["skills"].append(skill)

    goal = dynamic_model.get("current_goal")

    if goal:

        if goal not in prompt_context["goals"]:
            prompt_context["goals"].append(goal)

    return prompt_context