from typing import Literal
from pydantic import BaseModel
from langchain_core.messages import SystemMessage

from app.src.graphs.codeArchive.state import UnifiedState
from app.src.utils.prompts import load_prompt
from app.src.services.llm import get_llm_model
from app.src.utils.get_last_msg import extract_last_user_message

class RouteDecision(BaseModel):
    route: Literal["ingest", "archive"]

async def supervisor_router(state: UnifiedState):
    messages = state["messages"]

    # 마지막 user message 찾기
    # 이거 코드만 추출하도록 수정해야함
    # last_user_message = extract_last_user_message(messages)

    system_prompt = load_prompt("codeArchive","supervisor.md")



    # decision = await get_llm_model("gemini").with_structured_output(RouteDecision).ainvoke(
    #     [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": last_user_message},
    #     ]
    # )
    decision = await get_llm_model("gemini").with_structured_output(RouteDecision).ainvoke(
        [
            SystemMessage(content=system_prompt),
            *messages
        ]
    )

    return {"route": decision.route, "code": messages}