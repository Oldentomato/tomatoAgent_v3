from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from app.src.graphs.codeIngest.state import CodeIngestState
from app.src.nodes.code_ingest import (
    generate_code_summary_node,
    confirm_before_save_node,
    save_to_faiss_node,
)
from app.src.graphs.codeIngest.config import CODE_INGEST_NODES
from app.src.graphs.codeIngest.routing import route_by_save_choice





def code_ingest_build_graph():
    graph = StateGraph[CodeIngestState, None, CodeIngestState, CodeIngestState](CodeIngestState)

    # 노드 등록
    graph.add_node(CODE_INGEST_NODES.GENERATE_SUMMARY, generate_code_summary_node)
    graph.add_node(CODE_INGEST_NODES.CONFIRM, confirm_before_save_node)
    graph.add_node(CODE_INGEST_NODES.SAVE_TO_FAISS, save_to_faiss_node)

    # 시작점
    graph.set_entry_point(CODE_INGEST_NODES.GENERATE_SUMMARY)

    # generate_summary → 확인 노드(AG-UI에서 interrupt로 멈춤, 사용자 입력 후 재개)
    graph.add_edge(CODE_INGEST_NODES.GENERATE_SUMMARY, CODE_INGEST_NODES.CONFIRM)

    # confirm 이후 분기: should_save에 따라 SAVE_TO_FAISS 또는 END
    graph.add_conditional_edges(
        CODE_INGEST_NODES.CONFIRM,
        route_by_save_choice,
        {
            "save_to_faiss": CODE_INGEST_NODES.SAVE_TO_FAISS,
            "end": END,
        },
    )

    # save_to_faiss 끝나면 종료
    graph.add_edge(CODE_INGEST_NODES.SAVE_TO_FAISS, END)

    compiled = graph.compile(checkpointer=InMemorySaver())

    return compiled