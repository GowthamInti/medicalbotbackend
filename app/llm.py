from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from abc import ABC, abstractmethod
from typing import Union, List, Any
import logging
import httpx
from app.config import (
    LLMProvider,
    LLM_PROVIDER,
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL_NAME,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS
)

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, messages) -> str:
        """Generate a response using the LLM."""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> dict:
        """Get information about the LLM provider."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM provider is healthy."""
        pass


class ChatGroqProvider(BaseLLMProvider):
    """ChatGroq LLM provider implementation."""
    
    def __init__(self):
        """Initialize the ChatGroq provider."""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required for ChatGroq provider")
        
        self.llm = ChatOpenAI(
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
            model=GROQ_MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=30,
            max_retries=3
        )
        logger.info(f"ChatGroq provider initialized with model: {GROQ_MODEL_NAME}")
    
    async def generate_response(self, messages) -> str:
        """Generate a response using ChatGroq."""
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating ChatGroq response: {str(e)}")
            raise
    
    def get_provider_info(self) -> dict:
        """Get ChatGroq provider information."""
        return {
            "provider": "chatgroq",
            "model": GROQ_MODEL_NAME,
            "base_url": GROQ_BASE_URL,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "type": "cloud",
            "description": "ChatGroq cloud-based LLM inference"
        }
    
    async def health_check(self) -> bool:
        """Check ChatGroq API health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GROQ_BASE_URL}/models",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    timeout=10
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"ChatGroq health check failed: {str(e)}")
            return False


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(self):
        """Initialize the Ollama provider."""
        self.llm = ChatOllama(
            model=OLLAMA_MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
            temperature=TEMPERATURE,
        )
        logger.info(f"Ollama provider initialized with model: {OLLAMA_MODEL_NAME}")
    
    async def generate_response(self, messages) -> str:
        """Generate a response using Ollama."""
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating Ollama response: {str(e)}")
            raise
    
    def get_provider_info(self) -> dict:
        """Get Ollama provider information."""
        return {
            "provider": "ollama",
            "model": OLLAMA_MODEL_NAME,
            "base_url": OLLAMA_BASE_URL,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "type": "local",
            "description": "Ollama local LLM hosting"
        }
    
    async def health_check(self) -> bool:
        """Check Ollama server health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {str(e)}")
            return False


class LLMService:
    """Service class for managing LLM interactions with multiple providers."""
    
    def __init__(self, provider: str = None):
        """
        Initialize the LLM service with the specified provider.
        
        Args:
            provider: LLM provider to use. If None, uses LLM_PROVIDER from config.
        """
        self.provider_name = provider or LLM_PROVIDER
        self.provider = self._create_provider(self.provider_name)
        logger.info(f"LLM service initialized with provider: {self.provider_name}")
    
    def _create_provider(self, provider_name: str) -> BaseLLMProvider:
        """Create the appropriate LLM provider instance."""
        if provider_name == LLMProvider.CHATGROQ.value:
            return ChatGroqProvider()
        elif provider_name == LLMProvider.OLLAMA.value:
            return OllamaProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    async def generate_response(self, messages) -> str:
        """
        Generate a response using the configured LLM provider.
        
        Args:
            messages: List of messages or a single message to send to the LLM
            
        Returns:
            str: Generated response from the LLM
        """
        return await self.provider.generate_response(messages)
    
    def get_provider_info(self) -> dict:
        """Get information about the current LLM provider."""
        return self.provider.get_provider_info()
    
    async def health_check(self) -> bool:
        """Check if the current LLM provider is healthy."""
        return await self.provider.health_check()
    
    def switch_provider(self, new_provider: str) -> dict:
        """
        Switch to a different LLM provider at runtime.
        
        Args:
            new_provider: Name of the new provider to switch to
            
        Returns:
            dict: Information about the switch operation
        """
        try:
            old_provider = self.provider_name
            self.provider = self._create_provider(new_provider)
            self.provider_name = new_provider
            
            logger.info(f"Switched LLM provider from {old_provider} to {new_provider}")
            
            return {
                "success": True,
                "old_provider": old_provider,
                "new_provider": new_provider,
                "provider_info": self.get_provider_info()
            }
        except Exception as e:
            logger.error(f"Failed to switch provider to {new_provider}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "current_provider": self.provider_name
            }
    
    @staticmethod
    def get_available_providers() -> List[dict]:
        """Get list of all available LLM providers."""
        return [
            {
                "name": LLMProvider.CHATGROQ.value,
                "display_name": "ChatGroq",
                "type": "cloud",
                "description": "ChatGroq cloud-based LLM inference",
                "requires_api_key": True,
                "models": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
            },
            {
                "name": LLMProvider.OLLAMA.value,
                "display_name": "Ollama",
                "type": "local",
                "description": "Local Llama model hosting with Ollama",
                "requires_api_key": False,
                "models": ["llama3.2:1b", "llama3", "llama2", "codellama", "mistral", "neural-chat"]
            }
        ]


# Global LLM service instance
llm_service = LLMService()


# Provider factory function for easy switching
def create_llm_service(provider: str = None) -> LLMService:
    """
    Create a new LLM service instance with the specified provider.
    
    Args:
        provider: LLM provider to use
        
    Returns:
        LLMService: Configured LLM service instance
    """
    return LLMService(provider)