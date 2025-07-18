from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat
from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
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


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "ChatGroq Conversational Chatbot API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # You could add more sophisticated health checks here
        # like testing LLM connectivity, memory service status, etc.
        return {
            "status": "healthy",
            "service": "chatbot-api",
            "version": API_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting ChatGroq Conversational Chatbot API")
    logger.info(f"API Title: {API_TITLE}")
    logger.info(f"API Version: {API_VERSION}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down ChatGroq Conversational Chatbot API")