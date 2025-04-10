"""
MCP Orchestrator Framework

A generic and extensible Python framework for orchestrating multiple Model Context Protocols (MCPs).
"""

from mcp_orchestrator.protocols import MCP, ContextCombinationStrategy
from mcp_orchestrator.orchestrator import McpOrchestrator

__all__ = ["MCP", "ContextCombinationStrategy", "McpOrchestrator"]
