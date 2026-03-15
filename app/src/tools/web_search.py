from tavily import AsyncTavilyClient
from config.settings import TAVILY_API_KEY
from app.core.exception import WebSearchToolError
from langchain_core.tools import tool

@tool(aprse_docstring=True)
async def search(query: str, k: int = 5) -> str:
    """질문의 내용에 대해 잘 모를경우 이 도구를 사용하여 웹에서 검색

    Args:
        query (str): 사용자의 질문

    Returns:
        str: JSON 문자열 
    """
    # TODO: SerpAPI, Tavily, Bing, etc.
    # 현재는 더미 구현
    tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY) 

    try:
        # 여러 결과를 한번에 합쳐서 나오도록 수정
        result = await tavily_client.search(query)
        return result
    except:
        raise WebSearchToolError()
