"""
Send commands to Browser MCP using the Node.js script.
"""

import argparse
import asyncio
import logging
import subprocess
import sys
from typing import Optional

from mcp_orchestrator import McpOrchestrator
from mcp_orchestrator.orchestrator import ErrorPolicy
from mcp_orchestrator.strategies import SimpleConcatenationStrategy


class NodeBrowserMCP:
    """
    A Browser MCP implementation that uses a Node.js script to send commands.
    """
    
    def __init__(self):
        """Initialize the NodeBrowserMCP."""
        self.logger = logging.getLogger(__name__)
    
    async def get_context(self, query_data: str) -> str:
        """
        Send a command to the browser using the Node.js script.
        
        Args:
            query_data: The browser command to execute.
        
        Returns:
            The result of the command execution.
        """
        self.logger.info(f"Executing browser command: {query_data}")
        
        # Use the Node.js script to send the command
        process = subprocess.Popen(
            ["node", "browser_mcp_simple.js", query_data],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            self.logger.error(f"Error executing command: {stderr}")
            return f"Error: {stderr}"
        
        self.logger.info(f"Command executed successfully: {stdout}")
        return f"Command sent to browser: {query_data}\nOutput: {stdout}"
    
    async def update_context(self, response_data: str) -> None:
        """Update method (not implemented)."""
        pass


async def main():
    """Send a command to Browser MCP."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Send a command to Browser MCP")
    parser.add_argument("command", help="The browser command to execute")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("browser_mcp_command")
    
    logger.info(f"Sending command to Browser MCP: {args.command}")
    
    # Create the Browser MCP instance
    browser_mcp = NodeBrowserMCP()
    
    # Create the orchestrator
    orchestrator = McpOrchestrator(
        mcps=[browser_mcp],
        strategy=SimpleConcatenationStrategy(),
        error_policy=ErrorPolicy.FAIL_FAST,
        logger=logger,
    )
    
    # Execute the command
    result = await orchestrator.gather_and_combine_context(args.command)
    logger.info(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
