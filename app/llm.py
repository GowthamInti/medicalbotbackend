from langchain_openai import ChatOpenAI
from app.config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS
)
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service class for managing LLM interactions using ChatGroq API."""
    
    def __init__(self):
        """Initialize the LLM service with ChatGroq configuration."""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.llm = ChatOpenAI(
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=30,
            max_retries=3
        )
        logger.info(f"LLM service initialized with model: {MODEL_NAME}")
    
    def get_llm(self) -> ChatOpenAI:
        """Get the configured LLM instance."""
        return self.llm
    
    async def generate_response(self, messages) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            messages: List of messages or a single message to send to the LLM
            
        Returns:
            str: Generated response from the LLM
        """
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise


# Global LLM service instance
llm_service = LLMService()