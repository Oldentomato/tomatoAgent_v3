from langgraph.graph import END
from app.src.nodes.code_ingest import (
    generate_code_summary_node,
    confirm_before_save_node,
    save_to_faiss_node,
)
from app.src.graphs.codeIngest.routing import route_by_save_choice

def register_code_ingest(builder):
    builder.add_node("generate_summary", generate_code_summary_node)
    builder.add_node("confirm_save", confirm_before_save_node)
    builder.add_node("save_to_faiss", save_to_faiss_node)

    builder.add_edge("generate_summary", "confirm_save")

    builder.add_conditional_edges(
        "confirm_save", 
        route_by_save_choice,
        {
            "save_to_faiss": "save_to_faiss",
            "end": END,
        }
    )

    builder.add_edge("save_to_faiss", END)