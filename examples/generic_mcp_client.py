"""
Generic MCP client implementation for the MCP Orchestrator framework.

This example implements a generic MCP client that can be used to communicate
with any MCP server that follows the Model Context Protocol specification.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Union

import aiohttp
from mcp_orchestrator import McpOrchestrator
from mcp_orchestrator.orchestrator import ErrorPolicy
from mcp_orchestrator.strategies import SimpleConcatenationStrategy


class GenericMCPClient:
    """
    A generic client for communicating with MCP servers.
    
    This client follows the Model Context Protocol specification.
    """
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the GenericMCPClient.
        
        Args:
            base_url: The base URL of the MCP server.
        """
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    async def get_context(self, query: str) -> Dict[str, Any]:
        """
        Get context from the MCP server.
        
        Args:
            query: The query to send to the MCP server.
        
        Returns:
            The context from the MCP server.
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/context"
                payload = {"query": query}
                
                self.logger.debug(f"Sending request to {url} with payload: {payload}")
                
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.warning(f"Error from server: {error_text}")
                        return {
                            "status": "error",
                            "error": f"Server returned status {response.status}: {error_text}",
                            "query": query,
                        }
                    
                    result = await response.json()
                    self.logger.debug(f"Received response: {result}")
                    return result
        except Exception as e:
            self.logger.error(f"Error in get_context: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
            }


class GenericMCP:
    """
    A generic MCP implementation that follows the MCP Orchestrator protocol.
    
    This MCP can be used to communicate with any MCP server that follows
    the Model Context Protocol specification.
    """
    
    def __init__(self, client: GenericMCPClient):
        """
        Initialize the GenericMCP.
        
        Args:
            client: The client to use for communicating with the MCP server.
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    async def get_context(self, query_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get context from the MCP server.
        
        Args:
            query_data: The query to send to the MCP server.
                       Can be a string query or a dictionary with query details.
        
        Returns:
            The context from the MCP server.
        """
        try:
            if isinstance(query_data, str):
                query = query_data
            elif isinstance(query_data, dict) and "query" in query_data:
                query = query_data["query"]
            else:
                raise ValueError("Invalid query_data format")
            
            self.logger.info(f"Getting context for query: {query}")
            
            return await self.client.get_context(query)
        except Exception as e:
            self.logger.error(f"Error in get_context: {e}")
            raise
    
    async def update_context(self, response_data: Any) -> None:
        """
        Update the context on the MCP server.
        
        This method is not implemented for the GenericMCP as it may not
        be supported by all MCP servers.
        
        Args:
            response_data: The response data to use for updating the context.
        """
        self.logger.info("GenericMCP does not support context updates")


class BrowserMCPAdapter:
    """
    An adapter for the Browser MCP that follows the MCP Orchestrator protocol.
    
    This adapter translates between the Browser MCP API and the MCP Orchestrator protocol.
    """
    
    def __init__(self):
        """Initialize the BrowserMCPAdapter."""
        self.logger = logging.getLogger(__name__)
    
    async def get_context(self, query_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get context from the Browser MCP.
        
        Args:
            query_data: The browser automation command to execute.
                       Can be a string command or a dictionary with command details.
        
        Returns:
            The result of the browser automation.
        """
        try:
            if isinstance(query_data, str):
                command = query_data
            elif isinstance(query_data, dict) and "command" in query_data:
                command = query_data["command"]
            else:
                raise ValueError("Invalid query_data format")
            
            self.logger.info(f"Executing browser command: {command}")
            
            # Since we can't directly communicate with the Browser MCP server,
            # we'll simulate the response for demonstration purposes
            await asyncio.sleep(1)
            
            return {
                "status": "success",
                "message": f"Browser MCP would execute: {command}",
                "note": "This is a simulated response. In a real implementation, you would need to use the Browser MCP extension to execute commands.",
            }
        except Exception as e:
            self.logger.error(f"Error in get_context: {e}")
            raise
    
    async def update_context(self, response_data: Any) -> None:
        """
        Update the browser context.
        
        This method is not implemented for the Browser MCP as it typically
        doesn't support updating context.
        
        Args:
            response_data: The response data to use for updating the context.
        """
        self.logger.info("Browser MCP does not support context updates")


async def run_generic_mcp_example():
    """Run an example using the GenericMCP."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("generic_mcp_example")
    
    logger.info("Starting Generic MCP example")
    
    try:
        # Use the Browser MCP adapter
        browser_mcp = BrowserMCPAdapter()
        logger.info("Using Browser MCP adapter")
        
        # Initialize the orchestrator with the Browser MCP
        strategy = SimpleConcatenationStrategy()
        orchestrator = McpOrchestrator(
            mcps=[browser_mcp],
            strategy=strategy,
            error_policy=ErrorPolicy.CONTINUE,
            logger=logger,
        )
        
        # Define browser automation commands to execute
        commands = [
            "Go to google.com",
            "Search for 'Browser MCP'",
            "Take a screenshot of the current page",
            "Extract all links from the current page",
        ]
        
        # Execute each command and get the results
        for command in commands:
            logger.info(f"Executing command: {command}")
            result = await orchestrator.gather_and_combine_context(command)
            logger.info(f"Result: {result}")
            print("\n" + "="*50 + "\n")
            
            # Wait a bit between commands
            await asyncio.sleep(1)
    
    except Exception as e:
        logger.error(f"Error in Generic MCP example: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_generic_mcp_example())
