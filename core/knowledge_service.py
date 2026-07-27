import json

from core.knowledge import retrieve_semantic_memories
from core.understanding import build_user_model
from core.user_model import build_dynamic_model
from core.memory_policy import should_use_context, build_prompt_context

def get_knowledge(user_message):

    memories = retrieve_semantic_memories(user_message)

    memory_list = []
    
    for memory in memories:
        memory_list.append(memory[1])
    
    '''print("\n=== RETRIEVED MEMORIES ===")
    
    for memory in memory_list:
        print("-", memory)'''
    
    knowledge_graph = build_user_model(memory_list)
    
    '''print("\n=== KNOWLEDGE GRAPH ===")
    print(json.dumps(knowledge_graph, indent=4))'''
    
    dynamic_model = build_dynamic_model(
        knowledge_graph,
        user_message
    )
    
    '''print("\n=== USER MODEL ===")
    print(json.dumps(dynamic_model, indent=4))'''

    knowledge = {

            "knowledge_graph": knowledge_graph,

            "dynamic_model": dynamic_model,

            "should_use_context": should_use_context(user_message)

        }

    prompt_context = build_prompt_context(
        knowledge,
        user_message
    )

    '''print("\n=== PROMPT CONTEXT ===")
    print(prompt_context)'''
    
    return {

        "knowledge_graph": knowledge["knowledge_graph"],

        "dynamic_model": knowledge["dynamic_model"],

        "should_use_context": knowledge["should_use_context"],

        "prompt_context": prompt_context

    }