from langchain_groq import ChatGroq
from src.config.setting import settings

def get_groq_llm():
    chat_groq=ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        max_retries=settings.MAX_RETRIES
    )
    return chat_groq