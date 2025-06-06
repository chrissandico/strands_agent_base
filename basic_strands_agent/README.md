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

Run the agent interactively:

```bash
python -m basic_strands_agent.agent
```

Or import and use in your own code:

```python
from basic_strands_agent.agent import run_agent

response = run_agent("Hello, how are you?")
print(response.message)
```

## Features

- Uses Anthropic Claude 3.7 Sonnet via Amazon Bedrock with ARN-based model specification
- Minimal implementation with no additional tools
- Simple interactive interface when run directly
- Error handling for common issues
- Detailed logging with callback handler
- Trace attributes for better observability

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
