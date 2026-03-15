from app.src.graph.state import UnifiedState
from app.src.tools.rag_search import search as rag_search
from app.src.utils.get_tool_message import get_tool_from_message


async def rag_tool_node(state: UnifiedState) -> dict:
    """
    사내 코드 / 문서용 RAG 검색
    """
    messages = state["messages"]
    user_id = state["user_id"]
    rag_minio = state["rag_minio"]

    query = get_tool_from_message(messages)

    if query == None:
        return {"tool_result": None}

    result = await rag_search(query, user_id, rag_minio)

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
