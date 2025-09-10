"""
Simple LangGraph workflow for testing langgraph dev
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
import operator
import uuid

class State(TypedDict):
    messages: Annotated[list, operator.add]

def call_model(state: State):
    """Simple model call that echoes the last message"""
    messages = state["messages"]
    
    # Check if messages list is empty
    if not messages:
        return {"messages": [AIMessage(content="No messages to process")]}
    
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        response = f"Echo: {last_message.content}"
        return {"messages": [AIMessage(content=response)]}
    return {"messages": []}

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("agent", call_model)

# Add edges
workflow.add_edge("__start__", "agent")
workflow.add_edge("agent", END)

# Compile the graph (checkpointer handled by LangGraph API)
app = workflow.compile()

if __name__ == "__main__":
    # Test the workflow with proper thread_id
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = app.invoke(
        {"messages": [HumanMessage(content="Hello, LangGraph!")]}, 
        config=config
    )
    print("Workflow result:", result)
