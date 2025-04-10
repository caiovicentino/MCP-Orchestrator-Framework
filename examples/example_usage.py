"""
Example usage of the MCP Orchestrator framework.

This script demonstrates how to use the framework with example MCPs
and combination strategies.
"""

import asyncio
import json
import logging
from typing import Any, Dict

from mcp_orchestrator import McpOrchestrator
from mcp_orchestrator.orchestrator import ErrorPolicy
from mcp_orchestrator.strategies import SimpleConcatenationStrategy, DictionaryMergeStrategy
from mcp_orchestrator.strategies.dictionary import MergePolicy

from examples.example_mcps import AsyncMemoryMCP, AsyncVectorStoreMCP, AsyncAPIClientMCP


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp_orchestrator_example")


async def example_text_concatenation():
    """Example using text-based MCPs with SimpleConcatenationStrategy."""
    logger.info("Running text concatenation example")
    
    # Initialize MCPs
    memory_mcp = AsyncMemoryMCP()
    vector_mcp = AsyncVectorStoreMCP()
    
    # Initialize strategy
    strategy = SimpleConcatenationStrategy(separator="\n---\n")
    
    # Initialize orchestrator
    orchestrator = McpOrchestrator(
        mcps=[memory_mcp, vector_mcp],
        strategy=strategy,
        error_policy=ErrorPolicy.CONTINUE,
        logger=logger,
    )
    
    # Gather and combine context
    query = "Python"
    combined_context = await orchestrator.gather_and_combine_context(query)
    
    logger.info(f"Combined context for query '{query}':")
    print(combined_context)
    print("\n" + "="*50 + "\n")
    
    # Update context in memory MCP
    await orchestrator.propagate_update({"Python": "Python is a programming language."})
    
    # Gather and combine context again
    combined_context = await orchestrator.gather_and_combine_context("Python")
    
    logger.info(f"Combined context after update:")
    print(combined_context)
    print("\n" + "="*50 + "\n")


async def example_dictionary_merge():
    """Example using dictionary-based MCPs with DictionaryMergeStrategy."""
    logger.info("Running dictionary merge example")
    
    # Initialize MCPs
    api_mcp = AsyncAPIClientMCP()
    
    # Initialize strategy
    strategy = DictionaryMergeStrategy(merge_policy=MergePolicy.COMBINE_LISTS)
    
    # Initialize orchestrator
    orchestrator = McpOrchestrator(
        mcps=[api_mcp],
        strategy=strategy,
        error_policy=ErrorPolicy.FAIL_FAST,
        logger=logger,
    )
    
    # Gather and combine context
    query = {"endpoint": "weather"}
    combined_context = await orchestrator.gather_and_combine_context(query)
    
    logger.info(f"Combined context for query '{query}':")
    print(json.dumps(combined_context, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Update context in API MCP
    await orchestrator.propagate_update({
        "endpoint": "weather",
        "data": {"temperature": 30, "condition": "cloudy", "location": "Example City"},
    })
    
    # Gather and combine context again
    combined_context = await orchestrator.gather_and_combine_context(query)
    
    logger.info(f"Combined context after update:")
    print(json.dumps(combined_context, indent=2))
    print("\n" + "="*50 + "\n")


async def example_multiple_mcps():
    """Example using multiple MCPs with different return types."""
    logger.info("Running multiple MCPs example")
    
    # Initialize MCPs
    memory_mcp = AsyncMemoryMCP()
    vector_mcp = AsyncVectorStoreMCP()
    api_mcp = AsyncAPIClientMCP()
    
    # Custom strategy to handle different return types
    class CustomCombinationStrategy:
        def combine(self, contexts: list) -> Dict[str, Any]:
            result = {"sources": []}
            
            for i, context in enumerate(contexts):
                if isinstance(context, str):
                    # Handle string context (memory MCP)
                    result["memory_context"] = context
                elif isinstance(context, list):
                    # Handle list context (vector MCP)
                    result["vector_documents"] = context
                elif isinstance(context, dict) and "data" in context:
                    # Handle API context
                    result["api_data"] = context["data"]
                
                # Add to sources
                result["sources"].append({
                    "index": i,
                    "type": type(context).__name__,
                })
            
            return result
    
    # Initialize orchestrator with custom strategy
    orchestrator = McpOrchestrator(
        mcps=[memory_mcp, vector_mcp, api_mcp],
        strategy=CustomCombinationStrategy(),
        error_policy=ErrorPolicy.CONTINUE,
        logger=logger,
    )
    
    # Prepare queries for each MCP
    memory_query = "example"  # For memory MCP
    vector_query = "Python"   # For vector MCP
    api_query = {"endpoint": "news"}  # For API MCP
    
    # We need to handle different query types for different MCPs
    # This is a simple approach - in a real application, you might want
    # to implement a more sophisticated query routing mechanism
    
    # Gather context from memory MCP
    memory_context = await memory_mcp.get_context(memory_query)
    
    # Gather context from vector MCP
    vector_context = await vector_mcp.get_context(vector_query)
    
    # Gather context from API MCP
    api_context = await api_mcp.get_context(api_query)
    
    # Manually combine contexts using the strategy
    combined_context = orchestrator.strategy.combine([
        memory_context,
        vector_context,
        api_context,
    ])
    
    logger.info("Combined context from multiple MCPs:")
    print(json.dumps(combined_context, indent=2))
    print("\n" + "="*50 + "\n")


async def main():
    """Run all examples."""
    logger.info("Starting MCP Orchestrator examples")
    
    await example_text_concatenation()
    await example_dictionary_merge()
    await example_multiple_mcps()
    
    logger.info("All examples completed")


if __name__ == "__main__":
    asyncio.run(main())
