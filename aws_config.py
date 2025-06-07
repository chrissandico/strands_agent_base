"""
AWS Configuration Module

This module sets up AWS configuration for the Strands agent.
It ensures that AWS credentials and region are properly configured
before any boto3 clients are created.

It supports both local development (using .env files) and production
(using AWS Secrets Manager) environments.
"""

import os
import boto3
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file for local development
# This is a no-op in Lambda environment
load_dotenv()

# Enable OpenTelemetry tracing for Strands
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
os.environ["STRANDS_OTEL_ENABLE_CONSOLE_EXPORT"] = os.getenv("STRANDS_OTEL_ENABLE_CONSOLE_EXPORT", "true")

# Set default region if not already set
if not os.environ.get('AWS_DEFAULT_REGION'):
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    logger.info(f"Set default AWS region to {os.environ['AWS_DEFAULT_REGION']}")

# Determine if we're running in a Lambda environment
is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
if is_lambda:
    logger.info("Running in AWS Lambda environment")
else:
    logger.info("Running in local environment")

# Get AWS credentials from Secrets Manager or environment variables
try:
    # Import here to avoid circular imports
    # In Lambda, this will use Secrets Manager if available
    # In local development, it will fall back to environment variables
    from basic_strands_agent.secrets_manager import get_aws_credentials
    
    # Get credentials
    aws_credentials = get_aws_credentials()
    
    # Create a session with the credentials
    if aws_credentials.get('aws_access_key_id') and aws_credentials.get('aws_secret_access_key'):
        session = boto3.Session(
            aws_access_key_id=aws_credentials['aws_access_key_id'],
            aws_secret_access_key=aws_credentials['aws_secret_access_key'],
            region_name=aws_credentials['region_name']
        )
        logger.info("AWS session created with credentials from configuration")
    else:
        # Fall back to default credentials
        session = boto3.Session()
        logger.info("AWS session created with default credentials")
    
    # Verify credentials
    credentials = session.get_credentials()
    if credentials is None:
        logger.warning("No AWS credentials found. Please check your configuration.")
    else:
        # Log the region being used
        region = session.region_name
        logger.info(f"Using AWS region: {region}")
        
except ImportError:
    # secrets_manager module not available yet, fall back to environment variables
    logger.info("secrets_manager module not available, using environment variables")
    
    # Create a session to verify credentials
    session = boto3.Session()
    credentials = session.get_credentials()
    
    if credentials is None:
        logger.warning("No AWS credentials found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
    else:
        logger.info("AWS credentials found and configured successfully.")
        
        # Log the region being used
        region = session.region_name
        logger.info(f"Using AWS region: {region}")
except Exception as e:
    logger.error(f"Error configuring AWS: {str(e)}")
    raise

# Initialize Bedrock client with explicit region
try:
    bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
    logger.info("Bedrock client initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Bedrock client: {str(e)}")
    raise
