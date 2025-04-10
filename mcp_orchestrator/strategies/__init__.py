"""
Context combination strategies for the MCP Orchestrator framework.

This package contains implementations of various strategies for
combining context from multiple MCPs.
"""

from mcp_orchestrator.strategies.simple import SimpleConcatenationStrategy
from mcp_orchestrator.strategies.dictionary import DictionaryMergeStrategy

__all__ = ["SimpleConcatenationStrategy", "DictionaryMergeStrategy"]
