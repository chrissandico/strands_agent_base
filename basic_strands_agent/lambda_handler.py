"""
AWS Lambda Handler for Strands Agent

This module adapts the FastAPI application to work with AWS Lambda and Function URLs.
It preserves all functionality, including streaming responses.

It also handles secrets management using AWS Secrets Manager for secure
storage and retrieval of sensitive information.
"""

import os
import sys
import json
import logging
import time
from typing import Dict, Any, Optional

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AWS configuration first to ensure region is set before any boto3 clients are created
import aws_config

# Import secrets manager
from basic_strands_agent.secrets_manager import get_secret, clear_cache, is_lambda_environment

# Import the FastAPI app
from basic_strands_agent.api_example import app

# Import Mangum for Lambda integration
from mangum import Mangum
from mangum.types import LambdaContext

# Import AWS Lambda Powertools for better logging and tracing
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.utilities.typing import LambdaContext as PowertoolsContext

# Configure logging
logger = Logger(service="strands-agent-lambda")
tracer = Tracer(service="strands-agent-lambda")

# Secret cache TTL in seconds (5 minutes)
SECRET_CACHE_TTL = 300
_last_secret_refresh = 0

# Create Mangum handler with custom settings for streaming
# Note: lifespan="off" is important for Lambda to avoid startup/shutdown hooks
handler = Mangum(
    app,
    lifespan="off",
    api_gateway_base_path=None,
    custom_handlers={
        "http": {
            "stream": True,  # Enable streaming support
        }
    }
)

def refresh_secrets_if_needed() -> None:
    """
    Refresh the secrets cache if needed
    """
    global _last_secret_refresh
    
    # Only refresh if we're in a Lambda environment
    if not is_lambda_environment():
        return
    
    # Check if we need to refresh
    current_time = time.time()
    if current_time - _last_secret_refresh > SECRET_CACHE_TTL:
        logger.debug("Refreshing secrets cache")
        clear_cache()
        
        # Pre-load common secrets
        try:
            get_secret('aws-credentials')
            # Add other common secrets here as needed
        except Exception as e:
            logger.warning(f"Error pre-loading secrets: {str(e)}")
        
        _last_secret_refresh = current_time

@tracer.capture_lambda_handler
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    AWS Lambda handler function that processes API Gateway or Function URL events
    
    This handler preserves all functionality of the original FastAPI application,
    including streaming responses.
    
    Args:
        event: The Lambda event object
        context: The Lambda context object
        
    Returns:
        The Lambda response object
    """
    # Refresh secrets if needed
    refresh_secrets_if_needed()
    
    # Log the incoming event (excluding sensitive data)
    safe_event = {k: v for k, v in event.items() if k not in ["headers", "body"]}
    logger.info(f"Received event: {json.dumps(safe_event)}")
    
    # Add trace attributes
    tracer.put_annotation(key="service", value="strands-agent-lambda")
    tracer.put_annotation(key="environment", value=os.getenv("ENVIRONMENT", "development"))
    tracer.put_annotation(key="region", value=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
    
    try:
        # Check if this is a streaming request
        is_streaming = False
        if event.get("path") == "/stream" and event.get("httpMethod") == "POST":
            is_streaming = True
            logger.info("Handling streaming request")
        
        # Process the event with Mangum
        response = handler(event, context)
        
        # For streaming responses, ensure proper headers are set
        if is_streaming:
            if "headers" not in response:
                response["headers"] = {}
            
            # Set headers for streaming response
            response["headers"].update({
                "Content-Type": "text/plain",
                "Transfer-Encoding": "chunked",
                "X-Content-Type-Options": "nosniff"
            })
        
        return response
    
    except Exception as e:
        logger.exception(f"Error processing request: {str(e)}")
        
        # Return a proper error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": str(e),
                "message": "An error occurred processing the request"
            })
        }

# For local testing
if __name__ == "__main__":
    # Simulate a Lambda event for testing
    test_event = {
        "httpMethod": "POST",
        "path": "/chat",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "prompt": "Hello, how are you?"
        })
    }
    
    # Create a mock context
    class MockContext:
        function_name = "local-test"
        memory_limit_in_mb = 128
        invoked_function_arn = "arn:aws:lambda:local:0:function:local-test"
        aws_request_id = "local-test"
    
    # Process the event
    response = lambda_handler(test_event, MockContext())
    print(f"Response: {json.dumps(response, indent=2)}")
