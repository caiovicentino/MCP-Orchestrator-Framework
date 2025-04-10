# MCP Orchestrator Framework

A generic and extensible Python framework for orchestrating multiple Model Context Protocols (MCPs).

## Overview

This framework allows different projects to utilize and combine context from various sources (represented by MCP implementations) before interacting with a Large Language Model (LLM).

## Features

- Standardized MCP interface using Python's typing.Protocol
- Asynchronous operations support using asyncio
- Configurable context combination strategies
- Error handling policies
- Extensible design for adding new MCPs and strategies

## Requirements

- Python >= 3.8
- asyncio
- typing

## Installation

```bash
pip install -e .
```

## Usage

See the `examples` directory for complete usage examples.

Basic usage:

```python
import asyncio
from mcp_orchestrator import McpOrchestrator
from mcp_orchestrator.strategies import SimpleConcatenationStrategy
from your_mcps import YourCustomMcp1, YourCustomMcp2

async def main():
    # Initialize your MCPs
    mcp1 = YourCustomMcp1()
    mcp2 = YourCustomMcp2()
    
    # Choose a combination strategy
    strategy = SimpleConcatenationStrategy()
    
    # Create the orchestrator
    orchestrator = McpOrchestrator(mcps=[mcp1, mcp2], strategy=strategy)
    
    # Gather and combine context
    combined_context = await orchestrator.gather_and_combine_context(query_data="Your query")
    
    # Use the combined context with your LLM
    # ...

if __name__ == "__main__":
    asyncio.run(main())
```

## License

MIT
