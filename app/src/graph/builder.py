from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from app.src.graph.state import UnifiedState
from app.src.graph.routing import supervisor_router


from langgraph.graph import END

from app.src.nodes.search_approval_node import ask_search_method_node
from app.src.nodes.route_search import route_by_search_choice
# from app.src.nodes.rag_tool import rag_tool_node
# from app.src.nodes.web_tool import web_tool_node
from app.src.tools import web_search, rag_search
from langgraph.prebuilt import ToolNode, tools_condition
from app.src.nodes.answer import answer_node
from app.src.nodes.chat_history import load_chat_history, persist_chat_turn
from app.src.nodes.code_ingest import (
    generate_code_summary_node,
    confirm_before_save_node,
    save_to_faiss_node,
)
from app.src.graphs.codeIngest.routing import route_by_save_choice
from app.src.services.llm import get_llm_model


def code_archive_graph():
    builder = StateGraph(UnifiedState)

    builder.add_node("load_history", load_chat_history)
    builder.add_node("supervisor", supervisor_router)
    
    builder.set_entry_point("load_history")

    builder.add_edge("load_history", "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        lambda s: s["route"],
        {
            "ingest": "generate_summary",
            "archive": "condition_node",
        }
    )

    rag_search_with_minio = rag_search(rag_minio=rag_minio, rag_content_minio=rag_content_minio)

    search_tools = [web_search, rag_search_with_minio]

    llm = get_llm_model("gemini")
    llm_with_tools = llm.bind_tools(search_tools)


    # code ingest route
    builder.add_node("generate_summary", generate_code_summary_node)
    # builder.add_node("confirm_save", confirm_before_save_node) # 여기는 interrupt관련 개발완료되면 주석해제할것
    builder.add_node("save_to_faiss", save_to_faiss_node)

    builder.add_edge("generate_summary", "save_to_faiss")# 얘도 route 수정 해야함

    builder.add_conditional_edges(
        "confirm_save", 
        route_by_save_choice,
        {
            "save_to_faiss": "save_to_faiss",
            "end": END,
        }
    )

    builder.add_edge("save_to_faiss", END)


    # code retrieve route
    # builder.add_node("ask_search_method", ask_search_method_node)
    # builder.add_node("rag_tool", rag_tool_node)
    # builder.add_node("web_tool", web_tool_node)
    def condition_node(state):
        """
        여기서는 tool을 직접 실행하지 않는다.
        LLM이 tool을 쓸지 말지 판단해서 AIMessage를 만든다.
        """
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    builder.add_node("condition_node", condition_node)
    tool_node = ToolNode(search_tools)
    builder.add_node("tools", tool_node)
    builder.add_node("answer", answer_node)
    builder.add_node("persist", persist_chat_turn)


    # builder.add_conditional_edges(
    #     "ask_search_method",
    #     route_by_search_choice,
    #     {
    #         "rag": "rag_tool",
    #         "web": "web_tool",
    #         "end": END,
    #     }
    # )

    # agent 결과를 보고:
    # - tool call이 있으면 -> tools
    # - 없으면 -> END
    builder.add_conditional_edges(
        "condition_node",
        tools_condition,
        {
            "tools": "tools",
            "answer": "answer",
        },
    )

    # builder.add_edge("rag_tool", "answer")
    # builder.add_edge("web_tool", "answer")
    builder.add_edge("answer", "persist")
    builder.add_edge("persist", END)


    app = builder.compile(checkpointer=InMemorySaver())

    # print(app.get_graph().draw_mermaid())

    return app