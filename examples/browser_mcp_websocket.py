"""
WebSocket client for Browser MCP.

This script implements a WebSocket client for communicating with the Browser MCP server.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional, Union

import aiohttp
from mcp_orchestrator import McpOrchestrator
from mcp_orchestrator.orchestrator import ErrorPolicy
from mcp_orchestrator.strategies import SimpleConcatenationStrategy


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("browser_mcp_websocket")


class BrowserMCPWebSocketClient:
    """
    WebSocket client for communicating with the Browser MCP server.
    """
    
    def __init__(self, ws_url: str = "ws://localhost:9009/browser"):
        """
        Initialize the BrowserMCPWebSocketClient.
        
        Args:
            ws_url: The WebSocket URL of the Browser MCP server.
        """
        self.ws_url = ws_url
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.ws = None
        self.connected = False
        self.message_id = 0
        self.pending_requests = {}
    
    async def connect(self) -> bool:
        """
        Connect to the Browser MCP server.
        
        Returns:
            True if the connection was successful, False otherwise.
        """
        try:
            self.logger.info(f"Connecting to {self.ws_url}")
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(self.ws_url, timeout=10)
            self.connected = True
            self.logger.info("Connected to Browser MCP server")
            
            # Start the message handler
            asyncio.create_task(self._handle_messages())
            
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to Browser MCP server: {e}")
            if self.session:
                await self.session.close()
                self.session = None
            return False
    
    async def disconnect(self) -> None:
        """
        Disconnect from the Browser MCP server.
        """
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.connected = False
        self.logger.info("Disconnected from Browser MCP server")
    
    async def _handle_messages(self) -> None:
        """
        Handle incoming messages from the Browser MCP server.
        """
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        self.logger.debug(f"Received message: {data}")
                        
                        # Check if this is a response to a pending request
                        if "id" in data and data["id"] in self.pending_requests:
                            request_id = data["id"]
                            future = self.pending_requests[request_id]
                            future.set_result(data)
                            del self.pending_requests[request_id]
                        else:
                            self.logger.debug(f"Received unsolicited message: {data}")
                    except json.JSONDecodeError:
                        self.logger.warning(f"Received invalid JSON: {msg.data}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {msg}")
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    self.logger.info("WebSocket connection closed")
                    break
        except Exception as e:
            self.logger.error(f"Error handling messages: {e}")
        finally:
            self.connected = False
    
    async def send_command(self, command: str, timeout: float = 30.0) -> Dict[str, Any]:
        """
        Send a command to the Browser MCP server.
        
        Args:
            command: The command to send.
            timeout: The timeout in seconds.
        
        Returns:
            The response from the Browser MCP server.
        
        Raises:
            Exception: If the command fails.
        """
        if not self.connected:
            raise Exception("Not connected to Browser MCP server")
        
        # Create a message ID
        self.message_id += 1
        message_id = str(self.message_id)
        
        # Create a future to wait for the response
        future = asyncio.Future()
        self.pending_requests[message_id] = future
        
        # Create the message
        message = {
            "id": message_id,
            "command": command,
        }
        
        # Send the message
        await self.ws.send_json(message)
        self.logger.debug(f"Sent message: {message}")
        
        try:
            # Wait for the response
            response = await asyncio.wait_for(future, timeout)
            self.logger.debug(f"Received response: {response}")
            return response
        except asyncio.TimeoutError:
            del self.pending_requests[message_id]
            raise Exception(f"Timeout waiting for response to command: {command}")


class WebSocketBrowserMCP:
    """
    An implementation of the Browser MCP that uses WebSockets.
    
    This MCP communicates with the Browser MCP server using WebSockets.
    """
    
    def __init__(self, client: BrowserMCPWebSocketClient):
        """
        Initialize the WebSocketBrowserMCP.
        
        Args:
            client: The WebSocket client to use.
        """
        self.client = client
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
            
            # Send the command to the Browser MCP server
            response = await self.client.send_command(command)
            
            return response
        except Exception as e:
            self.logger.error(f"Error in get_context: {e}")
            return {
                "status": "error",
                "error": str(e),
                "command": command if "command" in locals() else str(query_data),
            }
    
    async def update_context(self, response_data: Any) -> None:
        """
        Update the browser context based on the response data.
        
        This method is not implemented for the Browser MCP as it typically
        doesn't support updating context.
        
        Args:
            response_data: The response data to use for updating the context.
        """
        self.logger.info("Browser MCP does not support context updates")


async def run_websocket_browser_mcp_example():
    """Run an example using the WebSocket Browser MCP."""
    logger.info("Starting WebSocket Browser MCP example")
    
    try:
        # Create the WebSocket client
        client = BrowserMCPWebSocketClient()
        
        # Connect to the Browser MCP server
        if not await client.connect():
            logger.error("Failed to connect to Browser MCP server")
            return
        
        try:
            # Create the Browser MCP
            browser_mcp = WebSocketBrowserMCP(client)
            
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
        finally:
            # Disconnect from the Browser MCP server
            await client.disconnect()
    
    except Exception as e:
        logger.error(f"Error in WebSocket Browser MCP example: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_websocket_browser_mcp_example())
