from langchain_openai import OpenAIEmbeddings
from app.config.settings import OPENAI_EMBEDDING_MODEL, OPENAI_API_KEY


embeddings = OpenAIEmbeddings(
    model=OPENAI_EMBEDDING_MODEL,
    api_key=OPENAI_API_KEY,
)
