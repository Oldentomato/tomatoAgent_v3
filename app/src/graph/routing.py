from typing import Literal
from pydantic import BaseModel

from app.src.graph.state import UnifiedState
from app.src.utils.prompts import load_prompt
from app.src.services.llm import get_llm_model
from app.src.utils.get_last_msg import extract_last_user_message

class RouteDecision(BaseModel):
    route: Literal["ingest", "archive"]

async def supervisor_router(state: UnifiedState):
    messages = state["messages"]

    # 마지막 user message 찾기
    last_user_message = extract_last_user_message(messages)

    system_prompt = load_prompt("supervisor.md")



    decision = await get_llm_model("gemini").with_structured_output(RouteDecision).ainvoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": last_user_message},
        ]
    )

    return {"route": decision.route, "code": last_user_message}