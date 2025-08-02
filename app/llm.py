from langchain_openai import ChatOpenAI
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
    TEMPERATURE,
    MAX_TOKENS
)
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory  # Optional, for type hinting

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
    
    async def generate_response(self, messages: list[dict], memory: ConversationBufferMemory = None) -> str:
        """
        Generate a response using ChatGroq with optional session memory.

        Args:
            messages: List of dicts like [{"role": "user", "content": "..."}]
            memory: Optional LangChain ConversationBufferMemory instance

        Returns:
            str: The response content from the model
        """
        try:
            # Extract the latest user message
            last_user_message = messages[-1]["content"]

            if memory:
                # Use LangChain conversation chain with memory (it tracks all context internally)
                chain = ConversationChain(llm=self.llm, memory=memory)
                return await chain.apredict(input=last_user_message)

            # No memory: convert to LangChain chat messages
            lc_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
                else:
                    raise ValueError(f"Unsupported role: {msg['role']}")

            # Direct call to LLM without memory
            response = await self.llm.ainvoke(lc_messages)
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


class LLMService:
    """Service class for managing LLM interactions with ChatGroq."""
    
    def __init__(self, provider: str = None):
        """
        Initialize the LLM service with the ChatGroq provider.
        
        Args:
            provider: LLM provider to use. Only 'chatgroq' is supported.
        """
        self.provider_name = provider or LLM_PROVIDER
        if self.provider_name != LLMProvider.CHATGROQ.value:
            raise ValueError(f"Only ChatGroq provider is supported. Got: {self.provider_name}")
        
        self.provider = ChatGroqProvider()
        logger.info(f"LLM service initialized with provider: {self.provider_name}")
    
    async def generate_response(self, input_message, memory=None) -> str:
        """
        Generate a response using the ChatGroq provider.

        Args:
            messages: List of messages (e.g., [{"role": "user", "content": "Hi"}])
            memory: Optional LangChain memory object

        Returns:
            str: Generated response from the LLM
        """
        return await self.provider.generate_response(input_message, memory)
    
    def get_provider_info(self) -> dict:
        """Get information about the ChatGroq provider."""
        return self.provider.get_provider_info()
    
    async def health_check(self) -> bool:
        """Check if the ChatGroq provider is healthy."""
        return await self.provider.health_check()
    
    @staticmethod
    def get_available_providers() -> List[dict]:
        """Get list of available LLM providers (only ChatGroq)."""
        return [
            {
                "name": LLMProvider.CHATGROQ.value,
                "display_name": "ChatGroq",
                "type": "cloud",
                "description": "ChatGroq cloud-based LLM inference",
                "requires_api_key": True,
                "models": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
            }
        ]


# Global LLM service instance
llm_service = LLMService()


# Provider factory function for consistency
def create_llm_service(provider: str = None) -> LLMService:
    """
    Create a new LLM service instance with the ChatGroq provider.
    
    Args:
        provider: LLM provider to use (only 'chatgroq' is supported)
        
    Returns:
        LLMService: Configured LLM service instance
    """
    return LLMService(provider)
