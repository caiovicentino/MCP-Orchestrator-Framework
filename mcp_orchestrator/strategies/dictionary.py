"""
Dictionary-based context combination strategies for the MCP Orchestrator framework.
"""

from enum import Enum
from typing import Any, Dict, List, Union


class MergePolicy(Enum):
    """Enum defining policies for handling key collisions during dictionary merging."""
    
    OVERWRITE = "overwrite"  # Later values overwrite earlier ones
    KEEP_FIRST = "keep_first"  # Keep the first value encountered
    COMBINE_LISTS = "combine_lists"  # Combine values into lists
    ERROR = "error"  # Raise an error on collision


class DictionaryMergeStrategy:
    """
    A strategy that merges dictionary-based contexts.
    
    This strategy assumes all contexts are dictionaries and merges them
    according to a specified policy for handling key collisions.
    """
    
    def __init__(self, merge_policy: MergePolicy = MergePolicy.OVERWRITE):
        """
        Initialize the DictionaryMergeStrategy.
        
        Args:
            merge_policy: The policy to follow when handling key collisions.
        """
        self.merge_policy = merge_policy
    
    def combine(self, contexts: List[Any]) -> Dict[str, Any]:
        """
        Combine multiple contexts by merging dictionaries.
        
        Args:
            contexts: A list of context data from different MCPs.
                     All contexts must be dictionaries.
        
        Returns:
            The merged dictionary.
        
        Raises:
            ValueError: If no contexts are provided or if any context is not a dictionary.
            KeyError: If a key collision occurs and the merge policy is ERROR.
        """
        if not contexts:
            raise ValueError("No contexts provided for combination")
        
        # Ensure all contexts are dictionaries
        for i, context in enumerate(contexts):
            if not isinstance(context, dict):
                raise ValueError(
                    f"Context at index {i} is not a dictionary: {type(context)}"
                )
        
        # Start with an empty result dictionary
        result: Dict[str, Any] = {}
        
        # Merge dictionaries according to the policy
        for context in contexts:
            for key, value in context.items():
                if key not in result:
                    # Key doesn't exist yet, simply add it
                    result[key] = value
                else:
                    # Key already exists, handle according to policy
                    if self.merge_policy == MergePolicy.OVERWRITE:
                        result[key] = value
                    elif self.merge_policy == MergePolicy.KEEP_FIRST:
                        # Do nothing, keep the existing value
                        pass
                    elif self.merge_policy == MergePolicy.COMBINE_LISTS:
                        # Convert to list if not already and append
                        if not isinstance(result[key], list):
                            result[key] = [result[key]]
                        
                        if isinstance(value, list):
                            result[key].extend(value)
                        else:
                            result[key].append(value)
                    elif self.merge_policy == MergePolicy.ERROR:
                        raise KeyError(
                            f"Key collision: '{key}' already exists in the result"
                        )
        
        return result
