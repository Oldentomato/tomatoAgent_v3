from graph.state import State
from src.services.llm import llm
from src.utils.prompts import load_prompt


TOOL_SELECTOR_PROMPT = load_prompt("tool_selector.md")


async def tool_selector_node(state: State) -> dict:
    """
    사용자 질문을 보고 사용할 tool을 결정한다.
    이 노드만 tool_choice를 설정할 수 있다.
    """
    last_user_message = state["messages"][-1]["content"]

    prompt = TOOL_SELECTOR_PROMPT.format(
        question=last_user_message
    )

    response = llm.invoke(prompt).strip().lower()

    # ---- 방어적 파싱 (중요) ----
    if response not in {
        "rag_code_search",
        "internet_search",
        "none",
    }:
        response = "none"

    tool_input = None
    if response != "none":
        tool_input = last_user_message

    return {
        "tool_choice": response,
        "tool_input": tool_input,
    }
