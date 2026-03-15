from typing import Optional
from copilotkit import CopilotKitState  # Base state class from CopilotKit
from app.minio.session_store import RAGSessionStore


class CodeIngestState(CopilotKitState):
    # List of available tools for the agent to use
    tools: list
    # Conversation history between user and assistant
    messages: list

    # 필수 입력
    code: str                  # 사용자가 넣은 소스 코드
    user_id: str               # 누구의 코드인지
    rag_minio: RAGSessionStore # Faiss index pickle 저장용 세션 스토어

    # 메타 정보 (선택)
    file_path: Optional[str]
    language: Optional[str]

    # 요약 관련
    auto_summary: Optional[str]   # LLM이 자동 생성한 설명
    final_summary: Optional[str]  # 사람이 확인/수정한 최종 설명

    # 저장 여부 (사람 입력)
    should_save: bool             # True면 faiss에 저장