from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import (
    LLMProviderResponse,
    AvailableProvidersResponse,
    LLMHealthResponse
)
from app.llm import llm_service, LLMService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get(
    "/provider",
    response_model=LLMProviderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current LLM provider information",
    description="""
    Retrieve information about the ChatGroq LLM provider.
    
    This endpoint provides details about:
    - Provider name (chatgroq)
    - Model being used
    - Configuration settings (temperature, max_tokens)
    - Provider type (cloud)
    - Base URL and connection details
    
    **Use Cases:**
    - Check provider configuration
    - Verify provider settings
    - Debugging and monitoring
    - Integration testing
    """,
    responses={
        200: {
            "description": "ChatGroq provider information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "current_provider": {
                            "provider": "chatgroq",
                            "model": "llama3-8b-8192",
                            "base_url": "https://api.groq.com/openai/v1",
                            "temperature": 0.7,
                            "max_tokens": 1024,
                            "type": "cloud",
                            "description": "ChatGroq cloud-based LLM inference"
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to retrieve provider information"
                    }
                }
            }
        }
    }
)
async def get_current_provider() -> LLMProviderResponse:
    """Get information about the ChatGroq provider."""
    try:
        provider_info = llm_service.get_provider_info()
        return LLMProviderResponse(current_provider=provider_info)
    except Exception as e:
        logger.error(f"Error getting provider info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider information"
        )


@router.get(
    "/providers",
    response_model=AvailableProvidersResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available LLM providers",
    description="""
    Retrieve information about the available LLM provider (ChatGroq).
    
    This endpoint provides information about:
    - ChatGroq provider details
    - Provider type (cloud)
    - Authentication requirements
    - Available models
    - Provider description and capabilities
    
    **Use Cases:**
    - Discover available LLM options
    - Check provider capabilities
    - Integration planning
    """,
    responses={
        200: {
            "description": "Available LLM provider information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "providers": [
                            {
                                "name": "chatgroq",
                                "display_name": "ChatGroq",
                                "type": "cloud",
                                "description": "ChatGroq cloud-based LLM inference",
                                "requires_api_key": True,
                                "models": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_available_providers() -> AvailableProvidersResponse:
    """Get list of available LLM providers."""
    try:
        providers = LLMService.get_available_providers()
        return AvailableProvidersResponse(providers=providers)
    except Exception as e:
        logger.error(f"Error getting available providers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available providers"
        )


@router.get(
    "/health",
    response_model=LLMHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check ChatGroq provider health",
    description="""
    Check the health status of the ChatGroq LLM provider.
    
    This endpoint verifies:
    - Provider connectivity and availability
    - API authentication
    - Server responsiveness
    - Model accessibility
    
    **Health Check Details:**
    
    #### ChatGroq
    - Tests API connectivity to ChatGroq servers
    - Validates API key authentication
    - Checks model availability
    
    **Use Cases:**
    - Monitor provider availability
    - Troubleshoot connection issues
    - Health monitoring for load balancers
    - Automated system checks
    """,
    responses={
        200: {
            "description": "Health check completed (status details in response)",
            "content": {
                "application/json": {
                    "examples": {
                        "healthy": {
                            "summary": "Healthy ChatGroq provider",
                            "value": {
                                "provider": "chatgroq",
                                "healthy": True
                            }
                        },
                        "unhealthy": {
                            "summary": "Unhealthy provider",
                            "value": {
                                "provider": "chatgroq",
                                "healthy": False,
                                "error": "Connection timeout to ChatGroq API"
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Health check failed due to internal error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to perform health check"
                    }
                }
            }
        }
    }
)
async def check_llm_health() -> LLMHealthResponse:
    """Check the health of the ChatGroq provider."""
    try:
        provider_info = llm_service.get_provider_info()
        is_healthy = await llm_service.health_check()
        
        response = LLMHealthResponse(
            provider=provider_info["provider"],
            healthy=is_healthy
        )
        
        if not is_healthy:
            response.error = f"Provider {provider_info['provider']} is not responding"
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking LLM health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform health check"
        )