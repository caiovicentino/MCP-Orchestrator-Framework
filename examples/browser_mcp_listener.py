"""
WebSocket listener for Browser MCP.

This script connects to the Browser MCP server and listens for messages.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional

import aiohttp


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("browser_mcp_listener")


async def listen_to_browser_mcp():
    """
    Connect to the Browser MCP server and listen for messages.
    """
    logger.info("Starting Browser MCP listener")
    
    # Define WebSocket endpoints to try
    ws_endpoints = [
        "ws://localhost:9009/",
        "ws://localhost:9009/browser",
        "ws://localhost:9009/mcp",
        "ws://localhost:9009/ws",
        "ws://localhost:9009/socket",
    ]
    
    for ws_url in ws_endpoints:
        try:
            logger.info(f"Connecting to {ws_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url) as ws:
                    logger.info(f"Connected to {ws_url}")
                    
                    # Send a simple ping message
                    ping_message = {"type": "ping"}
                    await ws.send_json(ping_message)
                    logger.info(f"Sent ping message: {ping_message}")
                    
                    # Listen for messages
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = json.loads(msg.data)
                                logger.info(f"Received message: {data}")
                            except json.JSONDecodeError:
                                logger.warning(f"Received invalid JSON: {msg.data}")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WebSocket error: {msg}")
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            logger.info("WebSocket connection closed")
                            break
        except Exception as e:
            logger.error(f"Error connecting to {ws_url}: {e}")
    
    logger.info("Browser MCP listener finished")


if __name__ == "__main__":
    asyncio.run(listen_to_browser_mcp())
