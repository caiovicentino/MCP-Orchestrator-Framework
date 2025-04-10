"""
Real Browser MCP test with the MCP Orchestrator framework.

This example attempts to communicate with an already running Browser MCP server
that has been connected through the browser extension.
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


class RealBrowserMCP:
    """
    A real implementation of the Browser MCP for browser automation.
    
    This MCP communicates with an already running Browser MCP server.
    """
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the RealBrowserMCP.
        
        Args:
            base_url: The base URL of the Browser MCP server.
        """
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    async def get_context(self, query_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get context from the browser based on the query.
        
        This method sends a command to the Browser MCP server to perform
        browser automation and returns the result.
        
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
            
            # Try to communicate with the Browser MCP server
            try:
                async with aiohttp.ClientSession() as session:
                    # The actual endpoint and payload structure may vary depending on the Browser MCP API
                    # This is a guess based on common MCP server patterns
                    url = f"{self.base_url}/execute"
                    payload = {"command": command}
                    
                    self.logger.debug(f"Sending request to {url} with payload: {payload}")
                    
                    async with session.post(url, json=payload, timeout=30) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            self.logger.warning(f"Error from server: {error_text}")
                            return {
                                "status": "error",
                                "error": f"Server returned status {response.status}: {error_text}",
                                "command": command,
                            }
                        
                        result = await response.json()
                        self.logger.debug(f"Received response: {result}")
                        return result
            except aiohttp.ClientError as e:
                self.logger.warning(f"HTTP error: {e}")
                return {
                    "status": "error",
                    "error": f"HTTP error: {str(e)}",
                    "command": command,
                }
            except asyncio.TimeoutError:
                self.logger.warning("Request timed out")
                return {
                    "status": "error",
                    "error": "Request timed out",
                    "command": command,
                }
            except Exception as e:
                self.logger.warning(f"Unexpected error: {e}")
                return {
                    "status": "error",
                    "error": f"Unexpected error: {str(e)}",
                    "command": command,
                }
        except Exception as e:
            self.logger.error(f"Error in get_context: {e}")
            raise
    
    async def update_context(self, response_data: Any) -> None:
        """
        Update the browser context based on the response data.
        
        This method is not implemented for the Browser MCP as it typically
        doesn't support updating context.
        
        Args:
            response_data: The response data to use for updating the context.
        """
        self.logger.info("Browser MCP does not support context updates")


async def run_browser_mcp_test():
    """Run a test using the real Browser MCP."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("browser_mcp_test")
    
    logger.info("Starting real Browser MCP test")
    
    try:
        # Try different ports that the Browser MCP server might be using
        ports_to_try = [3000, 8000, 8080, 9000]
        browser_mcp = None
        
        for port in ports_to_try:
            base_url = f"http://localhost:{port}"
            logger.info(f"Trying to connect to Browser MCP server at {base_url}")
            
            try:
                # Try to ping the server
                async with aiohttp.ClientSession() as session:
                    try:
                        # Try different endpoints that might exist
                        endpoints = ["/", "/ping", "/status", "/health"]
                        for endpoint in endpoints:
                            try:
                                async with session.get(f"{base_url}{endpoint}", timeout=2) as response:
                                    if response.status == 200:
                                        logger.info(f"Successfully connected to Browser MCP server at {base_url}{endpoint}")
                                        browser_mcp = RealBrowserMCP(base_url=base_url)
                                        break
                            except:
                                continue
                        
                        if browser_mcp:
                            break
                    except:
                        continue
            except:
                continue
        
        if not browser_mcp:
            logger.warning("Could not connect to Browser MCP server. Using fallback URL.")
            browser_mcp = RealBrowserMCP(base_url="http://localhost:3000")
        
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
            
            # Wait a bit between commands to allow the browser to process
            await asyncio.sleep(2)
    
    except Exception as e:
        logger.error(f"Error in Browser MCP test: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_browser_mcp_test())
