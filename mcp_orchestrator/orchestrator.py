"""
Core orchestrator implementation for the MCP Orchestrator framework.

This module contains the main orchestrator class that coordinates the
collection and combination of context from multiple MCPs.
"""

import asyncio
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from mcp_orchestrator.protocols import MCP, ContextCombinationStrategy


class ErrorPolicy(Enum):
    """Enum defining error handling policies for the orchestrator."""
    
    FAIL_FAST = "fail_fast"  # Fail if any MCP fails
    CONTINUE = "continue"    # Continue with partial results if some MCPs fail
    IGNORE = "ignore"        # Ignore errors and continue with successful results


class McpOrchestrator:
    """
    Main orchestrator class for coordinating multiple MCPs.
    
    This class is responsible for gathering context from multiple MCPs
    concurrently and combining the results using a specified strategy.
    """
    
    def __init__(
        self,
        mcps: Sequence[MCP],
        strategy: ContextCombinationStrategy,
        error_policy: ErrorPolicy = ErrorPolicy.CONTINUE,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the MCP Orchestrator.
        
        Args:
            mcps: A sequence of MCP instances to orchestrate.
            strategy: The strategy to use for combining contexts.
            error_policy: The policy to follow when MCPs encounter errors.
            logger: Optional logger for logging events and errors.
        
        Raises:
            ValueError: If no MCPs are provided or if the strategy is invalid.
        """
        if not mcps:
            raise ValueError("At least one MCP must be provided")
        
        self.mcps = mcps
        self.strategy = strategy
        self.error_policy = error_policy
        self.logger = logger or logging.getLogger(__name__)
    
    async def gather_and_combine_context(
        self, query_data: Any, timeout: Optional[float] = None
    ) -> Any:
        """
        Gather context from all MCPs concurrently and combine the results.
        
        Args:
            query_data: The query or parameters to pass to each MCP.
            timeout: Optional timeout in seconds for context gathering.
        
        Returns:
            The combined context data.
        
        Raises:
            Exception: If context gathering or combination fails, depending
                      on the error policy.
        """
        self.logger.debug(f"Gathering context with query: {query_data}")
        
        # Create tasks for each MCP
        tasks = [
            self._gather_context_from_mcp(i, mcp, query_data)
            for i, mcp in enumerate(self.mcps)
        ]
        
        # Gather results concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results based on error policy
        contexts, errors = self._process_results(results)
        
        if errors and self.error_policy == ErrorPolicy.FAIL_FAST:
            self.logger.error(f"Context gathering failed: {errors}")
            raise RuntimeError(f"Context gathering failed: {errors}")
        
        # Combine contexts using the strategy
        if not contexts:
            self.logger.warning("No contexts were successfully gathered")
            return None
        
        self.logger.debug(f"Combining {len(contexts)} contexts")
        return self.strategy.combine(contexts)
    
    async def propagate_update(self, response_data: Any) -> None:
        """
        Propagate an update to all MCPs that support the update_context method.
        
        Args:
            response_data: The response data to pass to each MCP.
        
        Raises:
            Exception: If update propagation fails, depending on the error policy.
        """
        self.logger.debug(f"Propagating update with response: {response_data}")
        
        # Create tasks for each MCP that supports update_context
        tasks = []
        for i, mcp in enumerate(self.mcps):
            if hasattr(mcp, "update_context"):
                tasks.append(self._update_context_in_mcp(i, mcp, response_data))
        
        if not tasks:
            self.logger.debug("No MCPs support update_context")
            return
        
        # Propagate updates concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results based on error policy
        _, errors = self._process_results(results)
        
        if errors and self.error_policy == ErrorPolicy.FAIL_FAST:
            self.logger.error(f"Update propagation failed: {errors}")
            raise RuntimeError(f"Update propagation failed: {errors}")
    
    async def _gather_context_from_mcp(
        self, index: int, mcp: MCP, query_data: Any
    ) -> Tuple[int, Any]:
        """
        Gather context from a single MCP.
        
        Args:
            index: The index of the MCP in the sequence.
            mcp: The MCP instance.
            query_data: The query or parameters to pass to the MCP.
        
        Returns:
            A tuple of (index, context_data).
        
        Raises:
            Exception: If context gathering fails.
        """
        try:
            self.logger.debug(f"Gathering context from MCP {index}")
            context = await mcp.get_context(query_data)
            self.logger.debug(f"Successfully gathered context from MCP {index}")
            return index, context
        except Exception as e:
            self.logger.error(f"Error gathering context from MCP {index}: {e}")
            raise
    
    async def _update_context_in_mcp(
        self, index: int, mcp: MCP, response_data: Any
    ) -> Tuple[int, None]:
        """
        Update context in a single MCP.
        
        Args:
            index: The index of the MCP in the sequence.
            mcp: The MCP instance.
            response_data: The response data to pass to the MCP.
        
        Returns:
            A tuple of (index, None).
        
        Raises:
            Exception: If context update fails.
        """
        try:
            self.logger.debug(f"Updating context in MCP {index}")
            await mcp.update_context(response_data)
            self.logger.debug(f"Successfully updated context in MCP {index}")
            return index, None
        except Exception as e:
            self.logger.error(f"Error updating context in MCP {index}: {e}")
            raise
    
    def _process_results(
        self, results: List[Union[Tuple[int, Any], Exception]]
    ) -> Tuple[List[Any], Dict[int, Exception]]:
        """
        Process the results of asyncio.gather.
        
        Args:
            results: The results from asyncio.gather.
        
        Returns:
            A tuple of (contexts, errors).
        """
        contexts = []
        errors = {}
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors[i] = result
            else:
                index, context = result
                contexts.append(context)
        
        if errors:
            error_msg = ", ".join(f"MCP {i}: {e}" for i, e in errors.items())
            self.logger.warning(f"Errors occurred during processing: {error_msg}")
        
        return contexts, errors
