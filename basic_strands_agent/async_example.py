"""
Async Iterator Example for Strands Agent

This module demonstrates how to use the async iterators provided by the Strands Agent
for streaming responses in asynchronous environments.
"""

import asyncio
import logging
from typing import Dict, Any, AsyncGenerator

# Import the agent and stream_agent_async function
import sys
import os
# Add the parent directory to sys.path to allow imports from the current directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Direct import from the agent module in the same directory
from agent import agent, stream_agent_async

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_events(events_generator) -> str:
    """
    Process events from the agent's async iterator and return the full response
    
    Args:
        events_generator: A coroutine that returns an async generator of events from the agent
        
    Returns:
        The full text response from the agent
    """
    full_response = ""
    tool_uses = []
    
    try:
        # Await the coroutine to get the actual async generator
        events = await events_generator
        async for event in events:
            # Handle text generation events
            if "data" in event:
                print(f"Text: {event['data']}", end="", flush=True)
                full_response += event["data"]
            
            # Handle tool use events
            elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                tool_name = event["current_tool_use"]["name"]
                tool_input = event["current_tool_use"].get("input", {})
                print(f"\nUsing tool: {tool_name} with input: {tool_input}")
                tool_uses.append({
                    "name": tool_name,
                    "input": tool_input
                })
            
            # Handle reasoning events
            elif "reasoning" in event and event.get("reasoning"):
                reasoning_text = event.get("reasoningText", "")
                print(f"\nReasoning: {reasoning_text[:50]}..." if len(reasoning_text) > 50 else reasoning_text)
            
            # Handle lifecycle events
            elif event.get("init_event_loop", False):
                print("\n🔄 Event loop initialized")
            elif event.get("start_event_loop", False):
                print("▶️ Event loop starting")
            elif event.get("start", False):
                print("📝 New cycle started")
            elif "message" in event:
                print(f"📬 New message created: {event['message']['role']}")
            elif event.get("complete", False):
                print("\n✅ Response complete")
            elif event.get("force_stop", False):
                print(f"\n🛑 Event loop force-stopped: {event.get('force_stop_reason', 'unknown reason')}")
    
    except Exception as e:
        logger.error(f"Error processing events: {str(e)}")
        print(f"\nError: {str(e)}")
    
    return full_response

async def interactive_async_chat() -> None:
    """
    Run an interactive async chat with the agent
    """
    print("Async Strands Agent Interactive Chat")
    print("Type 'exit' to quit")
    
    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                break
                
            print("Processing (async)...")
            await process_events(stream_agent_async(user_input))
    
    except KeyboardInterrupt:
        print("\nExiting agent...")
    except Exception as e:
        logger.error(f"Error in interactive chat: {str(e)}")
        print(f"\nUnexpected error: {str(e)}")
        print("Exiting agent...")

async def demo_multiple_queries() -> None:
    """
    Demonstrate processing multiple queries concurrently
    """
    print("Processing multiple queries concurrently...")
    
    queries = [
        "What is the capital of France?",
        "What is 2+2?",
        "Who wrote Romeo and Juliet?"
    ]
    
    # Create tasks for each query
    tasks = []
    for query in queries:
        print(f"Creating task for query: {query}")
        task = asyncio.create_task(process_events(stream_agent_async(query)))
        tasks.append((query, task))
    
    # Wait for all tasks to complete
    for query, task in tasks:
        try:
            response = await task
            print(f"\nQuery: {query}")
            print(f"Response: {response[:100]}..." if len(response) > 100 else response)
        except Exception as e:
            print(f"Error processing query '{query}': {str(e)}")

async def main() -> None:
    """
    Main function to run the examples
    """
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            await interactive_async_chat()
        elif sys.argv[1] == "--concurrent":
            await demo_multiple_queries()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Available options: --interactive, --concurrent")
    else:
        # Default to interactive mode
        await interactive_async_chat()

if __name__ == "__main__":
    asyncio.run(main())
