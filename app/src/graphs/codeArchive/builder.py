from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from app.src.graphs.codeArchive.state import UnifiedState



from langgraph.graph import END

# from app.src.nodes.search_approval_node import ask_search_method_node
# from app.src.nodes.route_search import route_by_search_choice
# from app.src.nodes.rag_tool import rag_tool_node
# from app.src.nodes.web_tool import web_tool_node
from app.src.graphs.codeArchive.tools import web_search, rag_search
from langgraph.prebuilt import ToolNode, tools_condition
from app.src.graphs.codeArchive.nodes.routing import supervisor_router
from app.src.graphs.codeArchive.nodes.answer import answer_node
from app.src.graphs.codeArchive.nodes.check_process import check_process_node
from app.src.graphs.codeArchive.nodes.chat_history import load_chat_history, persist_chat_turn
from app.src.graphs.codeArchive.nodes.code_ingest import (
    generate_code_summary_node,
    confirm_before_save_node,
    save_to_faiss_node,
)
from app.src.services.llm import get_llm_model


def code_archive_graph():
    builder = StateGraph(UnifiedState)

    # builder.add_node("load_history", load_chat_history)
    builder.add_node("supervisor", supervisor_router)
    
    builder.set_entry_point("supervisor")

    # builder.add_edge("load_history", "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        lambda s: s["route"],
        {
            "ingest": "generate_summary",
            "archive": "condition_node",
        }
    )


    search_tools = [web_search, rag_search]

    #tool node를 그냥 node로 변경하고 이 tool을 결정하는 코드를 함수화하여 util에 저장할것

    llm = get_llm_model("gemini")
    llm_with_tools = llm.bind_tools(search_tools)


    # code ingest route
    builder.add_node("generate_summary", generate_code_summary_node)
    builder.add_node("check_process_node", check_process_node)
    builder.add_node("save_to_faiss", save_to_faiss_node)

    builder.add_edge("generate_summary", "check_process_node")


    # builder.add_edge("save_to_faiss", END) #이미 check_process_node에서 route가 결정됨


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
    # builder.add_node("persist", persist_chat_turn)


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
    builder.add_edge("answer", END)
    # builder.add_edge("persist", END)


    app = builder.compile(checkpointer=InMemorySaver())

    # print(app.get_graph().draw_mermaid())

    return app