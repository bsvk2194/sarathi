"""
Memory Tool for SARATHI.

Exposes memory management capabilities through
the Tool System using the Knowledge Service.
"""

import core.knowledge_service as knowledge_service

from core.tools.base import Tool
from core.tools.response import ToolResponse


class MemoryTool(Tool):
    """
    Tool wrapper around the memory subsystem.
    """

    name = "memory"

    description = "Store, retrieve, update, and manage memories."

    # ---------- Memory CRUD ----------

    

    def remember(self, *args, **kwargs):

        result = knowledge_service.remember(*args, **kwargs)

        return ToolResponse(
            success=True,
            message="Memory stored successfully.",
            data=result
        )
    
    def get_all_memories(self):

        memories = knowledge_service.get_all_memories()

        return ToolResponse(
            success=True,
            message=f"Retrieved {len(memories)} memories.",
            data=memories
        )

    def search_memories(self, *args, **kwargs):

        result = knowledge_service.search_memories(
            *args,
            **kwargs
        )

        return ToolResponse(
            success=True,
            message="Memory search completed.",
            data=result
        )

    def forget_memory(self, *args, **kwargs):

        result = knowledge_service.forget_memory(
            *args,
            **kwargs
        )

        return ToolResponse(
            success=True,
            message="Memory forgotten successfully.",
            data=result
        )


    def forget_memories(self, *args, **kwargs):

        result = knowledge_service.forget_memories(
            *args,
            **kwargs
        )

        return ToolResponse(
            success=True,
            message="Matching memories forgotten successfully.",
            data=result
        )


    def update_memory(self, *args, **kwargs):

        result = knowledge_service.update_memory(
            *args,
            **kwargs
        )

        return ToolResponse(
            success=True,
            message="Memory updated successfully.",
            data=result
        )


    def update_memory_by_id(self, *args, **kwargs):

        result = knowledge_service.update_memory_by_id(
            *args,
            **kwargs
        )

        return ToolResponse(
            success=True,
            message="Memory updated successfully.",
            data=result
        )


    def retrieve_semantic_memories(self, *args, **kwargs):

        result = knowledge_service.retrieve_semantic_memories(
            *args,
            **kwargs
        )

        return ToolResponse(
            success=True,
            message="Relevant memories retrieved successfully.",
            data=result
        )


    def answer_from_memories(self, *args, **kwargs):

        result = knowledge_service.answer_from_memories(
            *args,
            **kwargs
        )

        return ToolResponse(
            success=True,
            message="Generated answer from stored memories.",
            data=result
        )
