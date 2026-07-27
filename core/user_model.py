def build_dynamic_model(knowledge_graph, current_query):
    """
    Builds a dynamic understanding of the user from
    the classified knowledge graph.
    """

    dynamic_model = {

        "current_project": None,

        "current_goal": None,

        "current_focus": None,

        "current_skills": [],

        "current_technologies": []

    }

    project_scores = {}

    for project in knowledge_graph.get("projects", []):
        project_scores[project] = 0


    query = current_query.lower()


    for project in knowledge_graph.get("projects", []):

        if project.lower() in query:

            project_scores[project] += 100


    relationships = knowledge_graph.get("relationships", [])


    for relation in relationships:

        if relation["relation"] == "uses":

            technology = relation["target"].lower()

            if technology in query:

                if relation["source"] in project_scores:
                    project_scores[relation["source"]] += 25


    '''print("\n=== PROJECT SCORES ===")
    for project, score in project_scores.items():
        print(f"{project}: {score}")'''


    if project_scores:

        current_project = max(
            project_scores,
            key=project_scores.get
        )

        if project_scores[current_project] > 0:

            dynamic_model["current_project"] = current_project
            dynamic_model["current_focus"] = current_project


    project = dynamic_model["current_project"]

    if project:

        for relation in relationships:

            if (
                relation["source"] == project
                and relation["relation"] == "uses"
            ):

                dynamic_model["current_technologies"].append(
                    relation["target"]
                )


    if knowledge_graph.get("goals"):

        dynamic_model["current_goal"] = knowledge_graph["goals"][0]


    dynamic_model["current_skills"] = knowledge_graph.get("skills", [])        

    return dynamic_model 