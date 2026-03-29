from sre_parse import State
from langgraph.types import Command, interrupt
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Literal
from langgraph.graph import END

from app.src.services.llm import get_llm_model

class RouteDecision(BaseModel):
    new_summary: str | None = Field(default=None, description="새로운 코드 설명을 제공해 줄 경우")
    route: Literal["save", "not_save"]

async def check_process_node(state: Dict[str, Any], config: RunnableConfig):
    # """
    # 이 노드는 요약한 코드내용을 수정, 혹은 저장 확인을 위한 사용자 인터럽트를 처리하고 최종 응답을 생성합니다.
    # 새로운 코드내용을 제공하면 그 내용을 이용하여 저장하도록 하세요.
    # 내용을 저장하지 않는다고 하면 그대로 대화를 종료하십시오.
    # """

    route_prompt = """
        당신은 현재 사용자의 입력에 따른 다음 행동의 결정을 내려야합니다.
        당신은 사용자에게 코드를 저장할 것인지 질문한 상태입니다.
        아래 두 가지의 선택지의 조건을 확인하고 적절한 결정을 선택해주세요.
        - save: 새로운 코드내용을 제공해주거나, 긍정적인 답변이 나왔을 경우
        - not_save: 부정적인 답변이 나왔을 경우

        다음 내용을 보고 적절한 답변을 해주고, **오직 위의 2가지 결정만을 답하세요.**
    """

    # Check if we already have a user_response in the state
    # This happens when the node restarts after an interrupt
    #이미 대화내역에 요청이 있을경우 그대로 진행
    # if "user_response" in state and state["user_response"]:
    #     user_response = state["user_response"]
    # else:#없을경우 interrupt를 통해 사용자의 답을 얻고 진행을함
    #     # Use LangGraph interrupt to get user input on steps
    #     # This will pause execution and wait for user input in the frontend
    #     user_response = interrupt({"auto_summary": state["auto_summary"]})
    #     # Store the user response in state for when the node restarts
    #     state["user_response"] = user_response

    # decision = await get_llm_model("gemini").with_structured_output(RouteDecision).ainvoke(
    #     [
    #         SystemMessage(content=route_prompt),
    #         user_response
    #     ]
    # )

    print(state)

    user_response = interrupt({"auto_summary": state["auto_summary"]})
    print(user_response)
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