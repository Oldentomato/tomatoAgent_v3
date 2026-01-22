from typing import TypedDict, Literal, Optional, List, Dict, Any


class State(TypedDict):
    # 대화 기록
    messages: List[Dict[str, Any]]

    # 어떤 tool을 사용할지 (단 하나)
    tool_choice: Literal[
        "rag_code_search",
        "internet_search",
        "none"
    ]

    # tool에 전달할 입력 (query)
    tool_input: Optional[str]

    # tool 실행 결과 (하나만 존재)
    tool_result: Optional[str]

    # 최종 답변
    final_answer: Optional[str]