from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from app.src.graphs.codeArchive.state import UnifiedState

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

    builder.add_node("load_history", load_chat_history) # neo4j에서 대화내역 가져오기
    builder.add_node("persist", persist_chat_turn) # neo4j로 대화내역 저장하기
    builder.add_node("supervisor", supervisor_router) #저장할지 검색할지 판단
    
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

    builder.add_edge("generate_summary", "check_process_node") # 이 내부에서 결정됨

    builder.add_edge("save_to_faiss", END) #check다음에 save로 가고 그다음은 끝냄(추후에 answer노드 따로만들것)


    # code retrieve route
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


    # 구조 변경
    # 먼저 archive에서 검색하고 그 결과를 분석
    # 사용자의 질문에 맞는 코드인거 같으면 그대로 출력
    # 그게 아니라면 아닌것 같다고 말하고 인터넷으로 검색할지 물어보는 노드를 추가(interrupt)
    builder.add_conditional_edges(
        "condition_node",
        tools_condition,
        {
            "tools": "tools",
            "answer": "answer",
        },
    )



    builder.add_edge("answer", END)
    # builder.add_edge("persist", END)


    app = builder.compile(checkpointer=InMemorySaver())

    # print(app.get_graph().draw_mermaid())

    return app