from langgraph.graph import StateGraph, END

from src.graph.state import State
from src.graph.config import NODES
from src.graph.routing import route_by_tool_choice

from src.nodes.tool_selector import tool_selector_node
from src.nodes.rag_tool import rag_tool_node
from src.nodes.web_tool import web_tool_node
from src.nodes.answer import answer_node


def build_graph():
    graph = StateGraph(State)

    # -----------------------------
    # 노드 등록
    # -----------------------------
    graph.add_node(NODES.TOOL_SELECTOR, tool_selector_node)
    graph.add_node(NODES.RAG_TOOL, rag_tool_node)
    graph.add_node(NODES.WEB_TOOL, web_tool_node)
    graph.add_node(NODES.ANSWER, answer_node)

    # -----------------------------
    # 시작점
    # -----------------------------
    graph.set_entry_point(NODES.TOOL_SELECTOR)

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
    graph.add_edge(NODES.ANSWER, END)

    return graph