from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.config import GEMINI_API_KEY

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def load_llm(model_name: str = "llama-3.1-8b-instant", gemini_api_key: str = GEMINI_API_KEY):
    try:
        logger.info("Loading LLM from Gemini using LLaMA3 model...")

        llm = ChatGoogleGenerativeAI(
            api_key=gemini_api_key,
            model=model_name
        )

        logger.info("LLM loaded successfully from Gemini.")
        return llm

    except Exception as e:
        error_message = CustomException("Failed to load an LLM from Gemini", e)
        logger.error(str(error_message))
        return None
