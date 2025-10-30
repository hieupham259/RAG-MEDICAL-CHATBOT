from langchain_huggingface import HuggingFaceEmbeddings

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)


def get_embeddings_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    try:
        logger.info(f"Loading embeddings model: {model_name}")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)

        logger.info("Huggingface embeddings model loaded successfully")
        return embeddings
    
    except Exception as e:
        error_message=CustomException("Error occured while loading embedding model" , e)
        logger.error(str(error_message))
        raise error_message