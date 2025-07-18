import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ChatGroq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3-8b-8192")

# LLM Configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# Memory Configuration
MEMORY_TTL_SECONDS = int(os.getenv("MEMORY_TTL_SECONDS", "3600"))  # 1 hour default
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))  # Max number of sessions

# FastAPI Configuration
API_TITLE = "ChatGroq Conversational Chatbot"
API_DESCRIPTION = "A FastAPI-based chatbot service using ChatGroq API for LLM inference"
API_VERSION = "1.0.0"