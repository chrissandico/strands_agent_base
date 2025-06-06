"""
FastAPI Example for Strands Agent

This module demonstrates how to use the Strands Agent with FastAPI
to create a streaming API endpoint.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys
import os
# Add the parent directory to sys.path to allow imports from the current directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Direct import from the agent module in the same directory
from agent import agent
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Strands Agent API",
    description="API for interacting with a Strands Agent",
    version="1.0.0"
)

class PromptRequest(BaseModel):
    """
    Request model for the prompt endpoint
    """
    prompt: str
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "What is the capital of France?"
            }
        }

@app.post("/stream")
async def stream_response(request: PromptRequest):
    """
    Stream the agent's response to a prompt
    
    Args:
        request: The prompt request
        
    Returns:
        A streaming response with the agent's output
    """
    logger.info(f"Received streaming request: {request.prompt}")
    
    async def generate():
        try:
            # Get the async iterator - no need to await the method itself
            async for event in agent.stream_async(request.prompt):
                if "data" in event:
                    # Only stream text chunks to the client
                    yield event["data"]
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            yield f"Error: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )

@app.post("/chat")
async def chat(request: PromptRequest):
    """
    Get a complete response from the agent
    
    Args:
        request: The prompt request
        
    Returns:
        The agent's complete response
    """
    logger.info(f"Received chat request: {request.prompt}")
    
    try:
        # Direct import from the agent module in the same directory
        from agent import run_agent
            
        response = run_agent(request.prompt)
        return {"response": response.message}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("basic_strands_agent.api_example:app", host="0.0.0.0", port=8000, reload=True)
