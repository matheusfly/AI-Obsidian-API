import logging
import os
from typing import Optional

# Set up logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging for the application"""
    logger = logging.getLogger("langgraph_obsidian")
    logger.setLevel(log_level)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(ch)
    
    return logger

# Basic tracing function
def trace_function_call(func_name: str, **kwargs):
    """Simple function to trace function calls"""
    logger = logging.getLogger("langgraph_obsidian.tracer")
    logger.info(f"Calling function: {func_name} with args: {kwargs}")

def trace_tool_execution(tool_name: str, parameters: dict, result: dict):
    """Trace MCP tool execution"""
    logger = logging.getLogger("langgraph_obsidian.tracer")
    logger.info(f"Executed tool: {tool_name} with parameters: {parameters}")
    logger.info(f"Tool result: {result}")

def trace_api_call(method: str, endpoint: str, status_code: int):
    """Trace API calls"""
    logger = logging.getLogger("langgraph_obsidian.tracer")
    logger.info(f"API call: {method} {endpoint} - Status: {status_code}")