"""
Simple context combination strategies for the MCP Orchestrator framework.
"""

from typing import Any, List


class SimpleConcatenationStrategy:
    """
    A simple strategy that concatenates text-based contexts.
    
    This strategy converts all contexts to strings and concatenates them
    with a separator.
    """
    
    def __init__(self, separator: str = "\n\n"):
        """
        Initialize the SimpleConcatenationStrategy.
        
        Args:
            separator: The separator to use between contexts.
        """
        self.separator = separator
    
    def combine(self, contexts: List[Any]) -> str:
        """
        Combine multiple contexts by concatenating them as strings.
        
        Args:
            contexts: A list of context data from different MCPs.
        
        Returns:
            The concatenated context as a string.
        
        Raises:
            ValueError: If no contexts are provided.
        """
        if not contexts:
            raise ValueError("No contexts provided for combination")
        
        # Convert all contexts to strings and join with the separator
        return self.separator.join(str(context) for context in contexts)
