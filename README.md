# AWS Lambda Strands Agent with Claude 3.7

A Strands agent implementation that uses Anthropic Claude 3.7 Sonnet via Amazon Bedrock with inference profile ARN, configured for secure deployment on AWS Lambda with Function URL.

## Security Best Practices for Secrets

This project demonstrates best practices for handling secrets (like AWS credentials) when deploying to Vercel:

1. **Never commit secrets to version control**
   - Use `.env` files for local development (added to `.gitignore`)
   - Use Vercel's Environment Variables for production

2. **Use environment variables for all secrets**
   - AWS credentials
   - API keys
   - Configuration values that differ between environments

3. **Separate example templates from actual secrets**
   - `.env.example` shows required variables without actual values
   - Actual `.env` file is git-ignored

## Local Development Setup

1. Install the required dependencies:

```bash
pip install -r basic_strands_agent/requirements.txt
```

2. Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

3. Edit the `.env` file with your actual AWS credentials:

```
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# Environment
ENVIRONMENT=development
```

4. Run the agent locally:

```bash
python -m basic_strands_agent.agent
```

## Deploying to AWS Lambda with Function URL

### Prerequisites

1. Install the AWS SAM CLI:

```bash
# For Windows (using pip)
pip install aws-sam-cli

# For macOS (using Homebrew)
brew install aws-sam-cli

# For Linux
pip install aws-sam-cli
```

2. Install Docker Desktop:
   - [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - [Docker for Linux](https://docs.docker.com/engine/install/)

3. Configure AWS credentials:

```bash
aws configure
```

### Deployment Options

This project includes enhanced deployment scripts that ensure cross-platform compatibility between Windows, macOS, Linux, and AWS Lambda's Linux environment:

#### For Windows:

```powershell
# Navigate to the deployment templates directory
cd deployment_templates

# Deploy to development environment
.\deploy.ps1 -env development

# Deploy to production with secrets
.\deploy.ps1 -env production -deploySecrets
```

#### For macOS/Linux:

```bash
# Navigate to the deployment templates directory
cd deployment_templates

# Make the script executable
chmod +x deploy.sh

# Deploy to development environment
./deploy.sh --env development

# Deploy to production with secrets
./deploy.sh --env production --deploy-secrets
```

#### Manual SAM Deployment:

```bash
# Navigate to the project directory
cd path/to/project

# Build the SAM application
sam build -t deployment_templates/sam-template.yaml

# Deploy the application
sam deploy --guided
```

### Cross-Platform Compatibility

The deployment scripts include several improvements to ensure compatibility between Windows and Lambda's Linux environment:

- **Docker-Based Dependency Installation**: Dependencies are installed in a Lambda-compatible environment
- **Package Optimization**: Unnecessary files are removed to reduce package size
- **Enhanced Error Handling**: Comprehensive error handling for more reliable deployments

For more details, see the [Deployment Improvements](docs/deployment_improvements.md) document.

4. Configure environment variables in AWS Lambda:
   - During the guided deployment, you'll be prompted for environment variables
   - Alternatively, you can set them in the AWS Lambda console:
     - Go to the AWS Lambda console
     - Select your function
     - Navigate to Configuration > Environment variables
     - Add the following variables:
       - `AWS_DEFAULT_REGION` (set automatically by Lambda)
       - `ENVIRONMENT` (set to "production")

5. Access your Lambda function via the Function URL:
   - The Function URL will be displayed in the outputs of the SAM deployment
   - You can also find it in the AWS Lambda console under Configuration > Function URL

## AWS Secrets Manager Integration

This project includes integration with AWS Secrets Manager for secure storage and retrieval of sensitive information:

1. **Automatic Environment Detection**
   - Automatically detects if running locally or in Lambda
   - Uses environment variables for local development
   - Uses AWS Secrets Manager for production environments

2. **Secure Credential Storage**
   - Stores AWS credentials in Secrets Manager
   - Supports JSON-formatted secrets for multiple values
   - Implements caching to minimize API calls

3. **Deployment Options**
   - CloudFormation template for creating secrets
   - Deployment scripts for managing secrets
   - Support for different environments (dev/staging/prod)

4. **Secret Rotation**
   - Supports automatic secret rotation
   - Handles secret rotation gracefully in the application
   - No code changes required when rotating secrets

## Secret Management Best Practices

1. **Regularly Rotate Credentials**
   - Use AWS Secrets Manager's rotation feature
   - Set up automatic rotation for production environments
   - Monitor rotation events with CloudTrail

2. **Use Least Privilege**
   - Create IAM roles with minimal permissions
   - Restrict access to secrets by environment
   - Use resource-based policies for additional security

3. **Monitor Access**
   - Enable CloudTrail logging for Secrets Manager
   - Set up alerts for unauthorized access attempts
   - Review access logs regularly

## Security Considerations

- Use IAM roles with least privilege for AWS credentials
- Create separate API keys for different environments
- Monitor AWS CloudTrail for unusual activity
- Consider using AWS Secrets Manager for more advanced secret management

## Using Claude 3.7 with Inference Profiles

This project demonstrates how to use Claude 3.7 with Bedrock inference profiles:

1. **Inference Profile ARN Format**
   - Claude 3.7 and newer models use inference profiles in Bedrock
   - The ARN format is: `arn:aws:bedrock:{region}:{account-id}:inference-profile/{model-id}:{version}`
   - Example: `arn:aws:bedrock:us-east-1:438465137422:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0`

2. **Implementation in Code**
   - Use the BedrockModel class from strands.models
   - Specify the full inference profile ARN as the model_id
   - Example:
   ```python
   from strands.models import BedrockModel
   
   bedrock_model = BedrockModel(
       model_id="arn:aws:bedrock:us-east-1:438465137422:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
       region_name='us-east-1'
   )
   
   agent = Agent(
       model=bedrock_model,
       # other parameters...
   )
   ```

3. **AWS Configuration**
   - Ensure your AWS credentials have access to the specified inference profile
   - Configure the AWS region correctly (us-east-1 for this example)
   - Request access to Claude 3.7 in the AWS Bedrock console if needed
