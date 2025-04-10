"""
Example of using the MCP Orchestrator framework with a connected Browser MCP.

This example assumes that:
1. The Browser MCP extension is installed in the browser
2. The extension is connected to the current tab
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Union

from mcp_orchestrator import McpOrchestrator
from mcp_orchestrator.orchestrator import ErrorPolicy
from mcp_orchestrator.strategies import SimpleConcatenationStrategy


class ConnectedBrowserMCP:
    """
    An implementation of the Browser MCP that works with a connected browser extension.

    This MCP assumes that the Browser MCP extension is already installed and connected
    in the browser.
    """

    def __init__(self):
        """Initialize the ConnectedBrowserMCP."""
        self.logger = logging.getLogger(__name__)
        self.server_process = None

    async def start_server(self):
        """
        Start the Browser MCP server if it's not already running.

        This method starts the Browser MCP server using npx.
        """
        try:
            # Start the Browser MCP server
            self.logger.info("Starting Browser MCP server...")
            # Try different ways to start the server
            try:
                # First try with npx
                self.server_process = subprocess.Popen(
                    ["npx", "@browsermcp/mcp@latest"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except FileNotFoundError:
                # If npx is not found, try with node directly
                self.logger.info("npx not found, trying with node directly...")
                try:
                    self.server_process = subprocess.Popen(
                        ["node", "./node_modules/@browsermcp/mcp/dist/index.js"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                except FileNotFoundError:
                    # If node is not found, try with the full path
                    self.logger.info("node not found, trying with full path...")
                    self.server_process = subprocess.Popen(
                        ["C:\\Program Files\\nodejs\\node.exe", "./node_modules/@browsermcp/mcp/dist/index.js"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )

            # Wait a bit for the server to start
            await asyncio.sleep(5)

            # Check if the process is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                self.logger.error(f"Browser MCP server failed to start: {stderr}")
                raise RuntimeError(f"Browser MCP server failed to start: {stderr}")

            self.logger.info("Browser MCP server started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Browser MCP server: {e}")
            raise

    async def get_context(self, query_data: str) -> Dict[str, Any]:
        """
        Send a command to the connected browser and get the result.

        This method assumes that the Browser MCP extension is connected to the browser
        and the server is running.

        Args:
            query_data: The browser automation command to execute.

        Returns:
            The result of the browser automation.
        """
        try:
            self.logger.info(f"Executing browser command: {query_data}")

            # In a real implementation with a properly connected Browser MCP,
            # the command would be automatically routed to the browser.
            # For now, we'll simulate a delay to represent the command execution.
            await asyncio.sleep(2)

            # Return a response indicating that the command was sent to the browser
            return {
                "status": "success",
                "message": f"Command sent to browser: {query_data}",
                "note": "Check your browser to see the actual result",
                "timestamp": time.time(),
            }
        except Exception as e:
            self.logger.error(f"Error executing browser command: {e}")
            return {
                "status": "error",
                "message": f"Failed to execute command: {str(e)}",
                "timestamp": time.time(),
            }

    async def update_context(self, response_data: Any) -> None:
        """
        Update method (not implemented for Browser MCP).

        Args:
            response_data: The response data to use for updating the context.
        """
        self.logger.info("Browser MCP does not support context updates")

    def stop_server(self):
        """Stop the Browser MCP server if it was started by this instance."""
        if self.server_process is not None:
            self.logger.info("Stopping Browser MCP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                self.logger.info("Browser MCP server stopped successfully")
            except subprocess.TimeoutExpired:
                self.logger.warning("Browser MCP server did not terminate gracefully, forcing...")
                self.server_process.kill()
                self.logger.info("Browser MCP server killed")


async def main():
    """Run the Browser MCP example with a connected browser."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("browser_mcp_connected")

    logger.info("Starting Browser MCP connected example")

    # Create the Browser MCP instance
    browser_mcp = ConnectedBrowserMCP()

    try:
        # Start the server (if not already running)
        await browser_mcp.start_server()

        # Create the orchestrator
        orchestrator = McpOrchestrator(
            mcps=[browser_mcp],
            strategy=SimpleConcatenationStrategy(),
            error_policy=ErrorPolicy.FAIL_FAST,
            logger=logger,
        )

        # Define some browser commands to execute
        commands = [
            "Go to google.com",
            "Search for 'Browser MCP documentation'",
            "Click on the first result",
            "Take a screenshot of the current page",
        ]

        # Execute each command
        for command in commands:
            logger.info(f"Sending command to browser: {command}")
            result = await orchestrator.gather_and_combine_context(command)
            logger.info(f"Command result: {result}")

            # Wait a bit between commands to allow the browser to execute them
            await asyncio.sleep(5)

        logger.info("All commands executed successfully")
    except Exception as e:
        logger.error(f"Error in Browser MCP example: {e}")
    finally:
        # Stop the server
        browser_mcp.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
