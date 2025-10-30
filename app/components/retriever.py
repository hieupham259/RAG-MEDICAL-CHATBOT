from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import PromptTemplate

from app.components.llm import load_llm
from app.components.vector_store import load_vector_store

from app.common.logger import get_logger
from app.common.custom_exception import CustomException


logger = get_logger(__name__)

CUSTOM_PROMPT_TEMPLATE = """ Answer the following medical question in 2-3 lines maximum using only the information provided in the context.

Context:
{context}

Question:
{question}

Answer:
"""

def set_custom_prompt():
    return PromptTemplate(template=CUSTOM_PROMPT_TEMPLATE, input_variables=["context", "question"])



def create_qa_chain():
    try:
        logger.info("Loading vector store for context")
        db = load_vector_store()

        if db is None:
            raise CustomException("Vector store not present or empty")

        llm = load_llm()

        if llm is None:
            raise CustomException("LLM not loaded")

        retriever = db.as_retriever(search_kwargs={'k': 3})
        
        if retriever is None:
            raise CustomException("Failed to create retriever tool")
        
        prompt = set_custom_prompt()

        # Create a proper QA chain that handles the question input correctly
        def format_docs_and_question(input_dict):
            question = input_dict["question"]
            docs = retriever.invoke(question)
            logger.info(f"Retrieved documents: {docs} from question: {question}")
            context = "\n".join([d.page_content for d in docs])
            return {"context": context, "question": question}

        qa_chain = RunnableSequence(
            format_docs_and_question
            | prompt
            | llm
        )

        logger.info("Successfully created the QA chain")
        return qa_chain

    except Exception as e:
        error_message = CustomException("Failed to make a QA chain", e)
        logger.error(str(error_message))
        return None


if __name__ == "__main__":
    try:
        logger.info("Starting QA chain execution...")
        
        # Create the QA chain
        qa_chain = create_qa_chain()
        
        if qa_chain is None:
            logger.error("Failed to create QA chain")
            exit(1)

        # Question about Chest drainage therapy
        question = "What is the purpose of Chest drainage therapy?"
        
        logger.info(f"Processing question: {question}")
        
        # Execute the QA chain
        response = qa_chain.invoke({"question": question})
        
        # Display results
        print("\n" + "="*60)
        print("RAG MEDICAL CHATBOT - QA CHAIN EXECUTION")
        print("="*60)
        print(f"Question: {question}")
        print(f"Answer: {response.content}")
        print("="*60 + "\n")
        
        logger.info("QA chain execution completed successfully")
        
    except Exception as e:
        error_message = CustomException("Failed to execute QA chain in main block", e)
        logger.error(str(error_message))
        print(f"Error: {str(error_message)}")