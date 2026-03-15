from langgraph.graph import END


from app.src.nodes.search_approval_node import ask_search_method_node
from app.src.nodes.route_search import route_by_search_choice
from app.src.nodes.rag_tool import rag_tool_node
from app.src.nodes.web_tool import web_tool_node
from app.src.nodes.answer import answer_node
from app.src.nodes.chat_history import load_chat_history, persist_chat_turn

def register_code_archive(builder):
    builder.add_node("load_history", load_chat_history)
    builder.add_node("ask_search_method", ask_search_method_node)
    builder.add_node("rag_tool", rag_tool_node)
    builder.add_node("web_tool", web_tool_node)
    builder.add_node("answer", answer_node)
    builder.add_node("persist", persist_chat_turn)

    builder.add_edge("load_history", "ask_search_method")

    builder.add_conditional_edges(
        "ask_search_method",
        route_by_search_choice,
        {
            "rag": "rag_tool",
            "web": "web_tool",
            "end": END,
        }
    )

    builder.add_edge("rag_tool", "answer")
    builder.add_edge("web_tool", "answer")
    builder.add_edge("answer", END)
    # builder.add_edge("persist", END)