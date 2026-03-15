from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from app.src.graphs.codeArchive.state import State
from app.src.graphs.codeArchive.config import NODES
from app.src.graphs.codeArchive.routing import route_by_tool_choice

from app.src.nodes.tool_selector import tool_selector_node
from app.src.nodes.rag_tool import rag_tool_node
from app.src.nodes.web_tool import web_tool_node
from app.src.nodes.answer import answer_node
from app.src.nodes.chat_history import load_chat_history, persist_chat_turn


#github 분석기


# 코드 검색기
def code_archive_build_graph():
    graph = StateGraph(State)

    # -----------------------------
    # 노드 등록
    # -----------------------------
    graph.add_node(NODES.LOAD_HISTORY, load_chat_history)
    graph.add_node(NODES.TOOL_SELECTOR, tool_selector_node)
    graph.add_node(NODES.RAG_TOOL, rag_tool_node)
    graph.add_node(NODES.WEB_TOOL, web_tool_node)
    graph.add_node(NODES.ANSWER, answer_node)
    graph.add_node(NODES.PERSIST, persist_chat_turn)

    # -----------------------------
    # 시작점
    # -----------------------------
    graph.set_entry_point(NODES.LOAD_HISTORY)
    graph.add_edge(NODES.LOAD_HISTORY, NODES.TOOL_SELECTOR)

    # -----------------------------
    # Tool 선택 분기
    # (배타적 사용을 구조적으로 강제)
    # -----------------------------
    graph.add_conditional_edges(
        NODES.TOOL_SELECTOR,
        route_by_tool_choice,
        {
            "rag_code_search": NODES.RAG_TOOL,
            "internet_search": NODES.WEB_TOOL,
            "none": NODES.ANSWER,
        }
    )

    # -----------------------------
    # Tool → Answer
    # -----------------------------
    graph.add_edge(NODES.RAG_TOOL, NODES.ANSWER)
    graph.add_edge(NODES.WEB_TOOL, NODES.ANSWER)

    # -----------------------------
    # 종료
    # -----------------------------
    graph.add_edge(NODES.ANSWER, NODES.PERSIST)
    graph.add_edge(NODES.PERSIST, END)

    graph = graph.compile(checkpointer=InMemorySaver())

    return graph