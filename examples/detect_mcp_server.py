"""
Script to detect and analyze MCP servers.

This script attempts to detect MCP servers running on various ports
and using various protocols.
"""

import asyncio
import json
import logging
import socket
import sys
import time
from typing import Dict, List, Optional, Tuple

import aiohttp


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("detect_mcp_server")


async def check_tcp_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Check if a TCP port is open.

    Args:
        host: The host to check.
        port: The port to check.
        timeout: The timeout in seconds.

    Returns:
        True if the port is open, False otherwise.
    """
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # Connect to the server
        result = sock.connect_ex((host, port))

        # Close the socket
        sock.close()

        # If result is 0, the port is open
        return result == 0
    except Exception as e:
        logger.debug(f"Error checking TCP port {port}: {e}")
        return False


async def check_http_endpoint(
    base_url: str, endpoint: str, timeout: float = 2.0
) -> Tuple[bool, Optional[Dict]]:
    """
    Check if an HTTP endpoint exists and returns a valid response.

    Args:
        base_url: The base URL of the server.
        endpoint: The endpoint to check.
        timeout: The timeout in seconds.

    Returns:
        A tuple of (success, response_data).
    """
    try:
        url = f"{base_url}{endpoint}"
        logger.debug(f"Checking HTTP endpoint: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        return True, data
                    except:
                        text = await response.text()
                        return True, {"text": text}
                else:
                    return False, None
    except Exception as e:
        logger.debug(f"Error checking HTTP endpoint {endpoint}: {e}")
        return False, None


async def check_websocket_endpoint(
    base_url: str, endpoint: str, timeout: float = 2.0
) -> bool:
    """
    Check if a WebSocket endpoint exists and accepts connections.

    Args:
        base_url: The base URL of the server.
        endpoint: The endpoint to check.
        timeout: The timeout in seconds.

    Returns:
        True if the WebSocket endpoint exists, False otherwise.
    """
    try:
        # Convert http:// to ws:// and https:// to wss://
        ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        url = f"{ws_url}{endpoint}"
        logger.debug(f"Checking WebSocket endpoint: {url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url, timeout=timeout) as ws:
                    # If we get here, the WebSocket connection was successful
                    await ws.close()
                    return True
        except:
            return False
    except Exception as e:
        logger.debug(f"Error checking WebSocket endpoint {endpoint}: {e}")
        return False


async def detect_mcp_servers():
    """
    Detect MCP servers running on various ports and using various protocols.
    """
    logger.info("Starting MCP server detection")

    # Define ports to check
    ports_to_check = [3000, 8000, 8080, 9000, 5000, 4000, 7000, 1234, 5678, 9009]

    # Define HTTP endpoints to check
    http_endpoints = [
        "/",
        "/ping",
        "/status",
        "/health",
        "/api",
        "/mcp",
        "/context",
        "/execute",
        "/browser",
    ]

    # Define WebSocket endpoints to check
    ws_endpoints = [
        "/",
        "/ws",
        "/socket",
        "/mcp",
        "/browser",
    ]

    # Check TCP ports
    logger.info("Checking TCP ports...")
    open_ports = []
    for port in ports_to_check:
        if await check_tcp_port("localhost", port):
            logger.info(f"Port {port} is open")
            open_ports.append(port)
        else:
            logger.debug(f"Port {port} is closed")

    if not open_ports:
        logger.info("No open ports found")

    # Check HTTP endpoints on open ports
    logger.info("Checking HTTP endpoints...")
    http_results = []
    for port in open_ports:
        base_url = f"http://localhost:{port}"
        for endpoint in http_endpoints:
            success, data = await check_http_endpoint(base_url, endpoint)
            if success:
                logger.info(f"HTTP endpoint {base_url}{endpoint} exists")
                http_results.append((base_url, endpoint, data))
            else:
                logger.debug(f"HTTP endpoint {base_url}{endpoint} does not exist")

    if not http_results:
        logger.info("No HTTP endpoints found")

    # Check WebSocket endpoints on open ports
    logger.info("Checking WebSocket endpoints...")
    ws_results = []
    for port in open_ports:
        base_url = f"http://localhost:{port}"
        for endpoint in ws_endpoints:
            if await check_websocket_endpoint(base_url, endpoint):
                logger.info(f"WebSocket endpoint {base_url.replace('http://', 'ws://')}{endpoint} exists")
                ws_results.append((base_url, endpoint))
            else:
                logger.debug(f"WebSocket endpoint {base_url.replace('http://', 'ws://')}{endpoint} does not exist")

    if not ws_results:
        logger.info("No WebSocket endpoints found")

    # Try to detect MCP servers based on the results
    logger.info("Analyzing results...")

    if not open_ports:
        logger.info("No MCP servers detected (no open ports)")
        return

    # Check if any HTTP endpoints returned MCP-related data
    mcp_servers = []
    for base_url, endpoint, data in http_results:
        if isinstance(data, dict):
            # Look for MCP-related keywords in the response
            response_str = json.dumps(data).lower()
            if any(keyword in response_str for keyword in ["mcp", "browser", "context", "model"]):
                logger.info(f"Potential MCP server detected at {base_url}{endpoint}")
                mcp_servers.append((base_url, endpoint, "HTTP", data))

    # Check if any WebSocket endpoints are likely MCP servers
    for base_url, endpoint in ws_results:
        if any(keyword in endpoint.lower() for keyword in ["mcp", "browser", "context", "model"]):
            logger.info(f"Potential MCP server detected at {base_url.replace('http://', 'ws://')}{endpoint}")
            mcp_servers.append((base_url, endpoint, "WebSocket", None))

    if not mcp_servers:
        logger.info("No MCP servers detected based on endpoint analysis")

    # Print summary
    logger.info("Detection complete")
    logger.info(f"Open ports: {open_ports}")
    logger.info(f"HTTP endpoints: {len(http_results)}")
    logger.info(f"WebSocket endpoints: {len(ws_results)}")
    logger.info(f"Potential MCP servers: {len(mcp_servers)}")

    for base_url, endpoint, protocol, data in mcp_servers:
        if protocol == "HTTP":
            logger.info(f"MCP server at {base_url}{endpoint} (HTTP)")
            logger.info(f"Response: {data}")
        else:
            logger.info(f"MCP server at {base_url.replace('http://', 'ws://')}{endpoint} (WebSocket)")


if __name__ == "__main__":
    asyncio.run(detect_mcp_servers())
