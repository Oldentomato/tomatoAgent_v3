from graph.state import State
from src.tools.web_search import search as web_search


async def web_tool_node(state: State) -> dict:
    """
    외부 인터넷 검색
    """
    query = state["tool_input"]
    if not query:
        return {"tool_result": None}

    result = await web_search(query)

    return {
        "tool_result": result,
        "messages": state["messages"] + [
            {
                "role": "tool",
                "name": "internet_search",
                "content": result,
            }
        ],
    }
