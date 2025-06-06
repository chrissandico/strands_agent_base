# Basic Strands Agent

A bare bones Strands agent implementation that uses Anthropic Claude 3.7 Sonnet via Amazon Bedrock with ARN-based model specification.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Configure your AWS credentials for Bedrock access:

```bash
# Set up AWS credentials
aws configure
# OR set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2  # or your preferred region
```

3. Make sure you have access to the model in Amazon Bedrock:
   - Go to the AWS Bedrock console
   - Request access to the Anthropic Claude models
   - Wait for approval (usually quick)

## Usage

### Run the agent interactively:

```bash
# Standard synchronous mode
python -m basic_strands_agent.agent

# Async streaming mode
python -m basic_strands_agent.agent --async
```

### Use in your code:

```python
# Synchronous usage
from basic_strands_agent.agent import run_agent

response = run_agent("Hello, how are you?")
print(response.message)

# Asynchronous usage with streaming
import asyncio
from basic_strands_agent.agent import stream_agent_async

async def example():
    agent_stream = stream_agent_async("Hello, how are you?")
    async for event in agent_stream:
        if "data" in event:
            print(event["data"], end="")

asyncio.run(example())
```

### Run the FastAPI server:

```bash
python -m basic_strands_agent.api_example
```

Then access the API at:
- http://localhost:8000/docs - API documentation
- POST to http://localhost:8000/stream - Streaming endpoint
- POST to http://localhost:8000/chat - Regular chat endpoint

### Advanced async examples:

```bash
# Interactive async chat
python -m basic_strands_agent.async_example --interactive

# Process multiple queries concurrently
python -m basic_strands_agent.async_example --concurrent
```

## Features

- Uses Anthropic Claude 3.7 Sonnet via Amazon Bedrock with ARN-based model specification
- Minimal implementation with no additional tools
- Simple interactive interface when run directly
- Error handling for common issues
- Detailed logging with callback handler
- Trace attributes for better observability
- Async iterators for streaming responses
- FastAPI integration for web applications

## Customization

You can easily modify the agent to use different models:

1. Edit `agent.py` to use a different model provider:
   - Uncomment and configure the alternative agent setup for OpenAI
   - Set the appropriate environment variables for API keys
   - Adjust model parameters as needed

2. Add tools by importing them and adding to the agent's tools list:
   ```python
   from strands_tools import calculator, current_time
   
   agent = Agent(
       # ... other settings ...
       tools=[calculator, current_time]
   )
   ```

## Troubleshooting

If you encounter errors:

1. Check your AWS credentials are properly configured
2. Verify you have access to the specified model in Bedrock
3. Try using a different model provider by modifying the agent configuration
4. Check the logs for detailed error information
