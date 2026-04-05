from typing import Optional, List, Dict, Any
from langgraph.graph import MessagesState


class UnifiedState(MessagesState):
    # List of available tools for the agent to use
    tools: list
    # Conversation history between user and assistant
    # messages: list

    tool_result: str

    steps: List[Dict[str, str]] = []
    tools: List[Any]

    # ingest
    code: str                  # 사용자가 넣은 소스 코드
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
