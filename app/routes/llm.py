from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import (
    LLMProviderResponse,
    AvailableProvidersResponse,
    SwitchProviderRequest,
    SwitchProviderResponse,
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
    Retrieve information about the currently active LLM provider.
    
    This endpoint provides details about:
    - Provider name (chatgroq, ollama)
    - Model being used
    - Configuration settings (temperature, max_tokens)
    - Provider type (cloud/local)
    - Base URL and connection details
    
    **Use Cases:**
    - Check which provider is currently active
    - Verify provider configuration
    - Debugging and monitoring
    - Integration testing
    """,
    responses={
        200: {
            "description": "Current LLM provider information retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "chatgroq": {
                            "summary": "ChatGroq provider active",
                            "value": {
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
                        },
                        "ollama": {
                            "summary": "Ollama provider active",
                            "value": {
                                "current_provider": {
                                    "provider": "ollama",
                                    "model": "llama3",
                                    "base_url": "http://localhost:11434",
                                    "temperature": 0.7,
                                    "max_tokens": 1024,
                                    "type": "local",
                                    "description": "Ollama local LLM hosting"
                                }
                            }
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
    """Get information about the current LLM provider."""
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
    summary="Get all available LLM providers",
    description="""
    Retrieve a list of all available LLM providers and their capabilities.
    
    This endpoint provides information about:
    - All supported providers (ChatGroq, Ollama)
    - Provider types (cloud vs local)
    - Authentication requirements
    - Available models for each provider
    - Provider descriptions and capabilities
    
    **Use Cases:**
    - Discover available LLM options
    - Check provider capabilities before switching
    - Display provider options in UI
    - Integration planning
    """,
    responses={
        200: {
            "description": "Available LLM providers retrieved successfully",
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
                            },
                            {
                                "name": "ollama",
                                "display_name": "Ollama",
                                "type": "local",
                                "description": "Local Llama model hosting with Ollama",
                                "requires_api_key": False,
                                "models": ["llama3", "llama2", "codellama", "mistral", "neural-chat"]
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_available_providers() -> AvailableProvidersResponse:
    """Get list of all available LLM providers."""
    try:
        providers = LLMService.get_available_providers()
        return AvailableProvidersResponse(providers=providers)
    except Exception as e:
        logger.error(f"Error getting available providers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available providers"
        )


@router.post(
    "/switch",
    response_model=SwitchProviderResponse,
    status_code=status.HTTP_200_OK,
    summary="Switch LLM provider at runtime",
    description="""
    Switch the active LLM provider at runtime without restarting the service.
    
    **Supported Providers:**
    - `chatgroq` - ChatGroq cloud API (requires API key)
    - `ollama` - Local Ollama server (requires Ollama to be running)
    
    **Provider Requirements:**
    
    #### ChatGroq
    - Valid GROQ_API_KEY environment variable
    - Internet connectivity
    - Active ChatGroq account
    
    #### Ollama
    - Ollama server running locally (default: http://localhost:11434)
    - Desired model pulled and available
    - Sufficient local resources (RAM/GPU)
    
    **Use Cases:**
    - Switch between cloud and local inference
    - Test different providers for comparison
    - Fallback to alternative provider if one fails
    - Dynamic provider selection based on requirements
    
    **Important Notes:**
    - Switch affects all new conversations globally
    - Existing conversations continue with their original provider until memory expires
    - Failed switches leave the current provider unchanged
    """,
    responses={
        200: {
            "description": "Provider switch completed (success or failure details in response)",
            "content": {
                "application/json": {
                    "examples": {
                        "success_to_ollama": {
                            "summary": "Successful switch to Ollama",
                            "value": {
                                "success": True,
                                "old_provider": "chatgroq",
                                "new_provider": "ollama",
                                "provider_info": {
                                    "provider": "ollama",
                                    "model": "llama3",
                                    "base_url": "http://localhost:11434",
                                    "temperature": 0.7,
                                    "max_tokens": 1024,
                                    "type": "local",
                                    "description": "Ollama local LLM hosting"
                                }
                            }
                        },
                        "success_to_chatgroq": {
                            "summary": "Successful switch to ChatGroq",
                            "value": {
                                "success": True,
                                "old_provider": "ollama",
                                "new_provider": "chatgroq",
                                "provider_info": {
                                    "provider": "chatgroq",
                                    "model": "llama3-8b-8192",
                                    "base_url": "https://api.groq.com/openai/v1",
                                    "temperature": 0.7,
                                    "max_tokens": 1024,
                                    "type": "cloud",
                                    "description": "ChatGroq cloud-based LLM inference"
                                }
                            }
                        },
                        "failure": {
                            "summary": "Failed provider switch",
                            "value": {
                                "success": False,
                                "error": "Ollama server not available at http://localhost:11434",
                                "current_provider": "chatgroq"
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid provider name",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid provider: unknown_provider. Available providers: chatgroq, ollama"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error during switch",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to switch provider due to internal error"
                    }
                }
            }
        }
    }
)
async def switch_provider(request: SwitchProviderRequest) -> SwitchProviderResponse:
    """Switch the active LLM provider at runtime."""
    try:
        # Validate provider name
        available_providers = [p["name"] for p in LLMService.get_available_providers()]
        if request.provider not in available_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider: {request.provider}. Available providers: {', '.join(available_providers)}"
            )
        
        # Attempt to switch provider
        result = llm_service.switch_provider(request.provider)
        
        if result["success"]:
            logger.info(f"Successfully switched LLM provider to {request.provider}")
        else:
            logger.warning(f"Failed to switch LLM provider to {request.provider}: {result.get('error')}")
        
        return SwitchProviderResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching provider: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch provider due to internal error"
        )


@router.get(
    "/health",
    response_model=LLMHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check LLM provider health",
    description="""
    Check the health status of the current LLM provider.
    
    This endpoint verifies:
    - Provider connectivity and availability
    - API authentication (for cloud providers)
    - Server responsiveness
    - Model accessibility
    
    **Health Check Details:**
    
    #### ChatGroq
    - Tests API connectivity to ChatGroq servers
    - Validates API key authentication
    - Checks model availability
    
    #### Ollama
    - Tests connection to local Ollama server
    - Verifies server is running and responsive
    - Checks if models are available
    
    **Use Cases:**
    - Monitor provider availability
    - Troubleshoot connection issues
    - Health monitoring for load balancers
    - Automated failover decisions
    """,
    responses={
        200: {
            "description": "Health check completed (status details in response)",
            "content": {
                "application/json": {
                    "examples": {
                        "healthy_chatgroq": {
                            "summary": "Healthy ChatGroq provider",
                            "value": {
                                "provider": "chatgroq",
                                "healthy": True
                            }
                        },
                        "healthy_ollama": {
                            "summary": "Healthy Ollama provider",
                            "value": {
                                "provider": "ollama",
                                "healthy": True
                            }
                        },
                        "unhealthy": {
                            "summary": "Unhealthy provider",
                            "value": {
                                "provider": "ollama",
                                "healthy": False,
                                "error": "Connection timeout to Ollama server at http://localhost:11434"
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
    """Check the health of the current LLM provider."""
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