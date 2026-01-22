from langchain_openai import ChatOpenAI
from app.config.settings import OPENAI_MODEL, OPENAI_API_KEY


llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0.1,
    api_key=OPENAI_API_KEY,
)
