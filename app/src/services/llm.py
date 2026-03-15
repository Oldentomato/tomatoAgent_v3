from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import OPENAI_MODEL, OPENAI_API_KEY, GEMINI_MODEL, GEMINI_API_KEY

__openai_llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0.1,
    api_key=OPENAI_API_KEY,
)

__gemini_llm = ChatGoogleGenerativeAI(
    model = GEMINI_MODEL,
    temperature=0.1,
    google_api_key=GEMINI_API_KEY
)

def get_llm_model(name: str):
    if name == "openai":
        return __openai_llm
    elif name == "gemini":
        return __gemini_llm
    else:
        raise 


