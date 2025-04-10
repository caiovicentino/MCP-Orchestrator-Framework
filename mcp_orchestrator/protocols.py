"""
Core protocols for the MCP Orchestrator framework.

This module defines the standard interfaces that all components must follow.
"""

from typing import Any, List, Protocol, runtime_checkable


@runtime_checkable
class MCP(Protocol):
    """
    Protocol defining the standard interface for Model Context Protocols.
    
    All MCP implementations must follow this interface to be compatible
    with the orchestrator.
    """
    
    async def get_context(self, query_data: Any) -> Any:
        """
        Asynchronously retrieve context based on the provided query data.
        
        Args:
            query_data: The query or parameters used to retrieve context.
                        The type depends on the specific MCP implementation.
        
        Returns:
            The context data. The type depends on the specific MCP implementation.
        
        Raises:
            Exception: If context retrieval fails.
        """
        ...
    
    async def update_context(self, response_data: Any) -> None:
        """
        Asynchronously update the context based on response data.
        
        This method is optional for MCP implementations. It allows for
        updating the context source based on the response from an LLM
        or other processing steps.
        
        Args:
            response_data: The response data used to update the context.
                          The type depends on the specific MCP implementation.
        
        Raises:
            Exception: If context update fails.
        """
        ...


@runtime_checkable
class ContextCombinationStrategy(Protocol):
    """
    Protocol defining the standard interface for context combination strategies.
    
    All context combination strategy implementations must follow this interface
    to be compatible with the orchestrator.
    """
    
    def combine(self, contexts: List[Any]) -> Any:
        """
        Combine multiple contexts into a single context.
        
        Args:
            contexts: A list of context data from different MCPs.
                     The types depend on the specific MCP implementations.
        
        Returns:
            The combined context data. The type depends on the specific
            strategy implementation.
        
        Raises:
            Exception: If context combination fails.
        """
        ...
