from src.graph.state import State
from src.tools.rag_search import search as rag_search


async def rag_tool_node(state: State) -> dict:
    """
    사내 코드 / 문서용 RAG 검색
    """
    query = state["tool_input"]
    if not query:
        return {"tool_result": None}

    result = await rag_search(query)

    return {
        "tool_result": result,
        "messages": state["messages"] + [
            {
                "role": "tool",
                "name": "rag_code_search",
                "content": result,
            }
        ],
    }
