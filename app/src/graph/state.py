from typing import TypedDict, Optional, List
from app.minio.session_store import RAGSessionStore
from app.repository.chat_repository import ChatRepository
from neo4j import AsyncGraphDatabase


class UnifiedState(TypedDict, total=False):
    # List of available tools for the agent to use
    tools: list
    # Conversation history between user and assistant
    messages: list

    tool_result: str

    # ingest
    code: str                  # 사용자가 넣은 소스 코드
    user_id: str               # 누구의 코드인지
    summary: str
    should_save: bool

    # archive
    history: List[str]
    search_choice: str

    auto_summary: Optional[str]   # LLM이 자동 생성한 설명
    final_summary: Optional[str]  # 사람이 확인/수정한 최종 설명

    # routing
    route: str

    tool_logs: list


                # tools=input_data.tools,
                # messages=input_data.messages,
                # code= "",
                # user_id="aaaa", #user_id 
                # rag_minio= rag_minio,
                # file_path= "",
                # language= "",
                # auto_summary= "",
                # final_summary= "",
                # should_save= True