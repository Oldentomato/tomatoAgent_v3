from langgraph.types import Command, interrupt
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Literal
from langgraph.graph import END
from copilotkit.langgraph import copilotkit_emit_state 

class RouteDecision(BaseModel):
    new_summary: str | None = Field(default=None, description="새로운 코드 설명을 제공해 줄 경우")
    route: Literal["save", "not_save"]

async def check_process_node(state: Dict[str, Any], config: RunnableConfig):
    # """
    # 이 노드는 요약한 코드내용을 수정, 혹은 저장 확인을 위한 사용자 인터럽트를 처리하고 최종 응답을 생성합니다.
    # 새로운 코드내용을 제공하면 그 내용을 이용하여 저장하도록 하세요.
    # 내용을 저장하지 않는다고 하면 그대로 대화를 종료하십시오.
    # """

    await copilotkit_emit_state(config, state) 

    payload = {
        "instruction": "요약을 확인하고, 수정이 필요하면 수정본을 넣어주세요.",
        "auto_summary": state.get("auto_summary")
    }

    user_response = interrupt(payload)
    print(f"user_response: {user_response}")
    new_summary = user_response["new_summary"] # or None
    save_route = user_response["save_allow"]

    
    if new_summary is not None:
        state["auto_summary"] = new_summary

    if save_route:
        return Command(
            goto="save_to_faiss"
        )

    elif not save_route:
        return Command(
            goto=END,
            update={
                "messages": AIMessage(content="저장하지 않고 종료합니다.")
            }
        )

    else:
        return Command(
            goto=END,
            update={
                "messages": AIMessage(content="AI의 답변에 문제가 발생했습니다. (위치: 저장 결정권)")
            }
        )