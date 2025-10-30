import os
from langchain_community.vectorstores import FAISS

from app.components.embeddings import get_embedding_model
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.config.config import DB_FAISS_PATH

logger = get_logger(__name__)

def load_vector_store():
    try:
        if not os.path.exists(DB_FAISS_PATH):
            raise CustomException("FAISS database path does not exist")
        
        logger.info(f"Loading FAISS vector store from {DB_FAISS_PATH}")
        embeddings = get_embedding_model()
        vector_store = FAISS.load_local(
            DB_FAISS_PATH, 
            embeddings,
            allow_dangerous_deserialization=True
        )

        logger.info("FAISS vector store loaded successfully")
        return vector_store
    
    except Exception as e:
        error_message = CustomException("Failed to load vectorstore" , e)
        logger.error(str(error_message))

# Creating new vectorstore function
def save_vector_store(text_chunks):
    try:
        if not text_chunks:
            raise CustomException("No chunks were found..")
        
        logger.info("Generating your new vectorstore")

        embedding_model = get_embedding_model()

        db = FAISS.from_documents(text_chunks,embedding_model)

        logger.info("Saving vectorstoree")

        db.save_local(DB_FAISS_PATH)

        logger.info("Vectostore saved sucesfulyy...")

        return db
    
    except Exception as e:
        error_message = CustomException("Failed to create new vectorstore", e)
        logger.error(str(error_message))