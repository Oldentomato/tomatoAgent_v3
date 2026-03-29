from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import OPENAI_EMBEDDING_MODEL, OPENAI_API_KEY, GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL


def get_embedding(name: str):
    if name == "openai":
        embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY,
        )
    elif name == "gemini":
        embeddings = GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            api_key=GEMINI_API_KEY,
        )
    else:
        raise 

    return embeddings