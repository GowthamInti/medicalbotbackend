from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, llm
from app.config import (
    API_TITLE, 
    API_DESCRIPTION, 
    API_VERSION, 
    API_CONTACT, 
    API_LICENSE, 
    API_TAGS_METADATA,
    SWAGGER_UI_PARAMETERS
)
from app.schemas.chat import HealthResponse, APIInfoResponse
from app.llm import llm_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application with enhanced documentation
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    contact=API_CONTACT,
    license_info=API_LICENSE,
    openapi_tags=API_TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters=SWAGGER_UI_PARAMETERS
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(llm.router)


@app.get(
    "/",
    response_model=APIInfoResponse,
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="API Information",
    description="""
    Get basic information about the ChatGroq Conversational Chatbot API.
    
    This endpoint provides:
    - API welcome message
    - Current version
    - Links to documentation
    - Health check endpoint
    
    **Perfect for:**
    - API discovery
    - Health monitoring
    - Integration testing
    - Service verification
    """,
    responses={
        200: {
            "description": "API information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "ChatGroq Conversational Chatbot API",
                        "version": "1.0.0",
                        "docs": "/docs",
                        "health": "/health",
                        "current_llm_provider": "chatgroq"
                    }
                }
            }
        }
    }
)
async def root() -> APIInfoResponse:
    """Root endpoint with API information."""
    try:
        current_provider = llm_service.get_provider_info()["provider"]
    except:
        current_provider = "chatgroq"
    
    return APIInfoResponse(
        message="ChatGroq Conversational Chatbot API",
        version=API_VERSION,
        docs="/docs",
        health="/health",
        current_llm_provider=current_provider
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Health Check",
    description="""
    Perform a health check on the ChatGroq Conversational Chatbot API.
    
    This endpoint verifies that:
    - The API service is running
    - Basic functionality is operational
    - Service metadata is accessible
    
    **Health Check Details:**
    - Returns 200 OK when service is healthy
    - Returns 503 Service Unavailable when service is unhealthy
    - Includes service name and version information
    
    **Monitoring Usage:**
    - Use this endpoint for load balancer health checks
    - Integrate with monitoring systems
    - Set up automated alerts for service availability
    """,
    responses={
        200: {
            "description": "Service is healthy and operational",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "chatbot-api",
                        "version": "1.0.0"
                    }
                }
            }
        },
        503: {
            "description": "Service is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Service unhealthy"
                    }
                }
            }
        }
    }
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        # Get LLM provider info and health status
        provider_info = llm_service.get_provider_info()
        llm_healthy = await llm_service.health_check()
        
        # Determine overall service health
        overall_status = "healthy" if llm_healthy else "degraded"
        
        return HealthResponse(
            status=overall_status,
            service="chatbot-api",
            version=API_VERSION,
            llm_provider=provider_info["provider"],
            llm_healthy=llm_healthy
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Service unhealthy"
        )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting ChatGroq Conversational Chatbot API")
    logger.info(f"API Title: {API_TITLE}")
    logger.info(f"API Version: {API_VERSION}")
    logger.info("Swagger UI available at: /docs")
    logger.info("ReDoc available at: /redoc")
    logger.info("OpenAPI JSON available at: /openapi.json")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down ChatGroq Conversational Chatbot API")