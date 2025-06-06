# Import AWS configuration first to ensure region is set before any boto3 clients are created
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import aws_config

from strands import Agent
from strands.models import BedrockModel
import logging
from dotenv import load_dotenv

# Load environment variables from .env file is already done in aws_config

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logging.getLogger("strands").setLevel(logging.DEBUG)

# Define a simple callback handler for logging
def callback_handler(**kwargs):
    if "data" in kwargs:
        # Log the streamed data chunks
        logging.info(kwargs["data"])
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        # Log tool usage information
        logging.info(f"Using tool: {kwargs['current_tool_use'].get('name')}")

# Create a BedrockModel with Claude 3.7 Sonnet inference profile ARN
bedrock_model = BedrockModel(
    model_id="arn:aws:bedrock:us-east-1:438465137422:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region_name='us-east-1'
)

# Define the agent with the BedrockModel
agent = Agent(
    model=bedrock_model,
    # No tools for bare bones version
    tools=[],
    system_prompt="You are a helpful assistant",
    # Simple callback handler for logging
    callback_handler=callback_handler,
    trace_attributes={
        "service": "basic-strands-agent",
        "version": "1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "model_provider": "anthropic",
        "model_name": "claude-3-7-sonnet",
        "region": os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    }
)

# Simple function to run the agent with a message
def run_agent(message):
    """
    Run the agent with the provided message
    
    Args:
        message (str): The message to send to the agent
        
    Returns:
        The agent's response or an error message
    """
    try:
        return agent(message)
    except Exception as e:
        logging.error(f"Error running agent: {str(e)}")
        return type('Response', (), {'message': f"Error: {str(e)}. Please check your AWS credentials and model access."})

async def stream_agent_async(message):
    """
    Stream the agent's response asynchronously
    
    Args:
        message (str): The message to send to the agent
        
    Returns:
        An async iterator that yields events from the agent
    """
    try:
        return agent.stream_async(message)
    except Exception as e:
        logging.error(f"Error streaming agent response: {str(e)}")
        # Re-raise to be handled by the caller
        raise

async def process_streaming_response(message):
    """
    Process a streaming response from the agent
    
    Args:
        message (str): The message to send to the agent
    """
    try:
        agent_stream = await stream_agent_async(message)
        async for event in agent_stream:
            if "data" in event:
                print(f"Text: {event['data']}")
            elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                print(f"Using tool: {event['current_tool_use']['name']}")
            elif "reasoning" in event and event.get("reasoning"):
                print(f"Reasoning: {event.get('reasoningText', '')[:50]}...")
            elif event.get("complete", False):
                print("Response complete")
    except Exception as e:
        print(f"Error processing streaming response: {str(e)}")

async def run_async_example():
    """
    Run an example of the async streaming functionality
    """
    print("Async Strands Agent Example")
    print("Type 'exit' to quit")
    
    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                break
                
            print("Processing (async)...")
            await process_streaming_response(user_input)
    except KeyboardInterrupt:
        print("\nExiting agent...")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("Exiting agent...")

# Example usage when script is run directly
if __name__ == "__main__":
    # Check if async mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--async":
        asyncio.run(run_async_example())
    else:
        print("Basic Strands Agent")
        print("Type 'exit' to quit")
        print("Note: This agent requires proper AWS credentials with Bedrock model access")
        print("      or appropriate API keys for other model providers.")
        print("      Run with --async flag to use async streaming mode")
        
        try:
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    break
                    
                print("Processing...")
                response = run_agent(user_input)
                print(f"\nAgent: {response.message}")
        except KeyboardInterrupt:
            print("\nExiting agent...")
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            print("Exiting agent...")
