"""
AWS Secrets Manager Module

This module provides functions for retrieving secrets from AWS Secrets Manager.
It falls back to environment variables when running locally or when secrets are not available.
"""

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Cache for secrets to minimize API calls
_secrets_cache: Dict[str, Any] = {}

def is_lambda_environment() -> bool:
    """
    Determine if the code is running in an AWS Lambda environment
    
    Returns:
        True if running in Lambda, False otherwise
    """
    return os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

def get_environment() -> str:
    """
    Get the current environment (development, staging, production)
    
    Returns:
        The environment name
    """
    return os.environ.get('ENVIRONMENT', 'development')

def get_secret_name(secret_id: str) -> str:
    """
    Get the full name of a secret based on the environment
    
    Args:
        secret_id: The base ID of the secret
        
    Returns:
        The full name of the secret
    """
    env = get_environment()
    return f"strands-agent-{env}-{secret_id}"

def get_secret(secret_id: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """
    Get a secret from AWS Secrets Manager
    
    Args:
        secret_id: The ID of the secret
        use_cache: Whether to use the cache
        
    Returns:
        The secret value as a dictionary, or None if not found
    """
    # Check cache first if enabled
    if use_cache and secret_id in _secrets_cache:
        return _secrets_cache[secret_id]
    
    # Only try to get secrets from AWS Secrets Manager if running in Lambda
    # or if AWS credentials are available
    if not is_lambda_environment() and not os.environ.get('AWS_ACCESS_KEY_ID'):
        logger.debug(f"Not in Lambda and no AWS credentials, skipping Secrets Manager for {secret_id}")
        return None
    
    # Get the full secret name
    secret_name = get_secret_name(secret_id)
    
    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        # Get the secret
        response = client.get_secret_value(SecretId=secret_name)
        
        # Parse the secret
        if 'SecretString' in response:
            secret = response['SecretString']
            try:
                # Try to parse as JSON
                secret_dict = json.loads(secret)
                if use_cache:
                    _secrets_cache[secret_id] = secret_dict
                return secret_dict
            except json.JSONDecodeError:
                # Not JSON, return as a dictionary with a single value
                secret_dict = {'value': secret}
                if use_cache:
                    _secrets_cache[secret_id] = secret_dict
                return secret_dict
        else:
            # Binary secret, not supported for now
            logger.warning(f"Binary secret not supported: {secret_name}")
            return None
            
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.warning(f"Secret not found: {secret_name}")
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            logger.warning(f"Access denied to secret: {secret_name}")
        else:
            logger.error(f"Error getting secret {secret_name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting secret {secret_name}: {str(e)}")
        return None

def get_secret_value(secret_id: str, key: str = None, default: Any = None, use_cache: bool = True) -> Any:
    """
    Get a specific value from a secret
    
    Args:
        secret_id: The ID of the secret
        key: The key of the value to get (if None, returns the entire secret)
        default: The default value to return if the secret or key is not found
        use_cache: Whether to use the cache
        
    Returns:
        The secret value, or the default if not found
    """
    secret = get_secret(secret_id, use_cache)
    
    if secret is None:
        return default
    
    if key is None:
        return secret
    
    return secret.get(key, default)

def get_aws_credentials() -> Dict[str, str]:
    """
    Get AWS credentials from Secrets Manager or environment variables
    
    Returns:
        A dictionary with AWS credentials
    """
    # Try to get from Secrets Manager first
    credentials = get_secret('aws-credentials')
    
    if credentials and 'aws_access_key_id' in credentials and 'aws_secret_access_key' in credentials:
        return {
            'aws_access_key_id': credentials['aws_access_key_id'],
            'aws_secret_access_key': credentials['aws_secret_access_key'],
            'region_name': credentials.get('aws_region', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        }
    
    # Fall back to environment variables
    return {
        'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'region_name': os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    }

def clear_cache() -> None:
    """
    Clear the secrets cache
    """
    _secrets_cache.clear()
    logger.debug("Secrets cache cleared")
