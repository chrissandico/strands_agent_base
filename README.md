# Vercel Strands Agent with Claude 3.7

A Strands agent implementation that uses Anthropic Claude 3.7 Sonnet via Amazon Bedrock with inference profile ARN, configured for secure deployment on Vercel.

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

## Deploying to Vercel

1. Install the Vercel CLI:

```bash
npm install -g vercel
```

2. Login to Vercel:

```bash
vercel login
```

3. Deploy to Vercel:

```bash
vercel
```

4. Configure environment variables in Vercel:
   - Go to the Vercel dashboard
   - Select your project
   - Navigate to Settings > Environment Variables
   - Add the following variables:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `AWS_DEFAULT_REGION`
     - `ENVIRONMENT` (set to "production")

5. Redeploy with the environment variables:

```bash
vercel --prod
```

## Secret Rotation Best Practices

1. Regularly rotate your AWS credentials
2. Update the rotated credentials in Vercel's environment variables
3. No code changes required when rotating secrets

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
