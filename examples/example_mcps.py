"""
Example MCP implementations for demonstration purposes.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional


class AsyncMemoryMCP:
    """
    An example MCP that retrieves context from an in-memory store.
    
    This is a simple implementation for demonstration purposes.
    """
    
    def __init__(self, memory_store: Optional[Dict[str, str]] = None):
        """
        Initialize the AsyncMemoryMCP.
        
        Args:
            memory_store: Optional pre-populated memory store.
        """
        self.memory_store = memory_store or {
            "default": "This is default memory context.",
            "example": "This is an example memory entry.",
            "test": "This is a test memory entry.",
        }
    
    async def get_context(self, query_data: str) -> str:
        """
        Asynchronously retrieve context from the memory store.
        
        Args:
            query_data: The key to look up in the memory store.
        
        Returns:
            The context string if found, or a default message.
        """
        # Simulate async operation
        await asyncio.sleep(0.1)
        
        # Look up the query in the memory store
        return self.memory_store.get(
            query_data, f"No memory found for query: {query_data}"
        )
    
    async def update_context(self, response_data: Dict[str, str]) -> None:
        """
        Asynchronously update the memory store.
        
        Args:
            response_data: A dictionary mapping keys to values to update.
        """
        # Simulate async operation
        await asyncio.sleep(0.1)
        
        # Update the memory store
        self.memory_store.update(response_data)


class AsyncVectorStoreMCP:
    """
    An example MCP that simulates retrieving context from a vector store.
    
    This is a simple implementation for demonstration purposes.
    """
    
    def __init__(self):
        """Initialize the AsyncVectorStoreMCP."""
        # Simulate a vector store with pre-embedded documents
        self.documents = [
            {"id": 1, "content": "Vector store document about Python programming."},
            {"id": 2, "content": "Vector store document about asyncio in Python."},
            {"id": 3, "content": "Vector store document about type hints in Python."},
            {"id": 4, "content": "Vector store document about MCPs and LLMs."},
        ]
    
    async def get_context(self, query_data: str) -> List[Dict[str, Any]]:
        """
        Asynchronously retrieve context from the simulated vector store.
        
        Args:
            query_data: The query to search for in the vector store.
        
        Returns:
            A list of matching documents.
        """
        # Simulate async operation and vector search
        await asyncio.sleep(0.2)
        
        # Simple keyword matching (in a real implementation, this would be a vector similarity search)
        matching_docs = [
            doc for doc in self.documents
            if any(term.lower() in doc["content"].lower() for term in query_data.split())
        ]
        
        return matching_docs or [{"id": 0, "content": f"No documents found for query: {query_data}"}]
    
    # This MCP doesn't implement update_context as it's read-only


class AsyncAPIClientMCP:
    """
    An example MCP that simulates retrieving context from an external API.
    
    This is a simple implementation for demonstration purposes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AsyncAPIClientMCP.
        
        Args:
            api_key: Optional API key for authentication.
        """
        self.api_key = api_key or "demo_api_key"
        # Simulate API responses
        self.api_responses = {
            "weather": {"temperature": 25, "condition": "sunny", "location": "Example City"},
            "news": [
                {"title": "Example News 1", "summary": "This is an example news item."},
                {"title": "Example News 2", "summary": "This is another example news item."},
            ],
            "user": {"name": "Example User", "email": "user@example.com"},
        }
    
    async def get_context(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously retrieve context from the simulated API.
        
        Args:
            query_data: A dictionary containing the endpoint and any parameters.
        
        Returns:
            The API response as a dictionary.
        
        Raises:
            ValueError: If the endpoint is not specified or is invalid.
        """
        if not isinstance(query_data, dict) or "endpoint" not in query_data:
            raise ValueError("Query data must be a dictionary with an 'endpoint' key")
        
        endpoint = query_data["endpoint"]
        
        # Simulate async API call
        await asyncio.sleep(0.3)
        
        # Check if the endpoint exists
        if endpoint not in self.api_responses:
            return {"error": f"Endpoint '{endpoint}' not found"}
        
        # Return the simulated API response
        return {
            "status": "success",
            "data": self.api_responses[endpoint],
            "endpoint": endpoint,
        }
    
    async def update_context(self, response_data: Dict[str, Any]) -> None:
        """
        Asynchronously update the API (simulated).
        
        Args:
            response_data: A dictionary containing the endpoint and data to update.
        
        Raises:
            ValueError: If the endpoint is not specified or is invalid.
        """
        if not isinstance(response_data, dict) or "endpoint" not in response_data or "data" not in response_data:
            raise ValueError("Response data must be a dictionary with 'endpoint' and 'data' keys")
        
        endpoint = response_data["endpoint"]
        data = response_data["data"]
        
        # Simulate async API call
        await asyncio.sleep(0.3)
        
        # Update the simulated API response
        if endpoint in self.api_responses:
            self.api_responses[endpoint] = data
