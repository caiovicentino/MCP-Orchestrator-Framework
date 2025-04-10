"""
Simple example to go to Google.com using the Browser MCP.
"""

import asyncio
import logging
import subprocess
import time
from typing import Any, Dict

from mcp_orchestrator import McpOrchestrator
from mcp_orchestrator.orchestrator import ErrorPolicy
from mcp_orchestrator.strategies import SimpleConcatenationStrategy


class SimpleBrowserMCP:
    """A simple Browser MCP implementation to go to Google.com."""
    
    def __init__(self):
        """Initialize the SimpleBrowserMCP."""
        self.logger = logging.getLogger(__name__)
        self.server_process = None
    
    async def start_server(self):
        """Start the Browser MCP server."""
        try:
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
            
            # Wait for the server to start
            await asyncio.sleep(5)
            self.logger.info("Browser MCP server started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Browser MCP server: {e}")
            raise
    
    async def get_context(self, query_data: str) -> Dict[str, Any]:
        """Send a command to the browser."""
        self.logger.info(f"Executing browser command: {query_data}")
        
        # Simulate a delay for the command execution
        await asyncio.sleep(2)
        
        return {
            "status": "success",
            "message": f"Command sent to browser: {query_data}",
            "note": "Check your browser to see the actual result",
            "timestamp": time.time(),
        }
    
    async def update_context(self, response_data: Any) -> None:
        """Update method (not implemented)."""
        pass
    
    def stop_server(self):
        """Stop the Browser MCP server."""
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
    """Go to Google.com using the Browser MCP."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("go_to_google")
    
    logger.info("Starting Browser MCP to go to Google.com")
    
    # Create the Browser MCP instance
    browser_mcp = SimpleBrowserMCP()
    
    try:
        # Start the server
        await browser_mcp.start_server()
        
        # Create the orchestrator
        orchestrator = McpOrchestrator(
            mcps=[browser_mcp],
            strategy=SimpleConcatenationStrategy(),
            error_policy=ErrorPolicy.FAIL_FAST,
            logger=logger,
        )
        
        # Go to Google.com
        command = "Go to google.com"
        logger.info(f"Sending command to browser: {command}")
        result = await orchestrator.gather_and_combine_context(command)
        logger.info(f"Command result: {result}")
        
        # Wait a bit to see the result
        logger.info("Waiting 10 seconds to see the result...")
        await asyncio.sleep(10)
        
        logger.info("Command executed successfully")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Stop the server
        browser_mcp.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
