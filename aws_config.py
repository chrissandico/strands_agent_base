"""
AWS Configuration Module

This module sets up AWS configuration for the Strands agent.
It ensures that AWS credentials and region are properly configured
before any boto3 clients are created.
"""

import os
import boto3
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable OpenTelemetry tracing for Strands
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
os.environ["STRANDS_OTEL_ENABLE_CONSOLE_EXPORT"] = os.getenv("STRANDS_OTEL_ENABLE_CONSOLE_EXPORT", "true")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set default region if not already set
if not os.environ.get('AWS_DEFAULT_REGION'):
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    logger.info(f"Set default AWS region to {os.environ['AWS_DEFAULT_REGION']}")

# Verify AWS credentials are available
try:
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
