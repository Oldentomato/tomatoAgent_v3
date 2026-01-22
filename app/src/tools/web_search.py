from tavily import AsyncTavilyClient
from config.settings import TAVILY_API_KEY
from app.core.exception import WebSearchToolError


async def search(query: str, k: int = 5) -> str:
    """
    외부 인터넷 검색
    (예시는 placeholder)
    """
    # TODO: SerpAPI, Tavily, Bing, etc.
    # 현재는 더미 구현
    tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY) 

    try:
        # 여러 결과를 한번에 합쳐서 나오도록 수정
        result = tavily_client.search(query)
        return result
    except:
        raise WebSearchToolError()
