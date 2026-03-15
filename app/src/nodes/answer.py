from app.src.graph.state import UnifiedState
from app.src.services.llm import get_llm_model
from app.src.utils.prompts import load_prompt


ANSWER_PROMPT = load_prompt("answer.md")


async def answer_node(state: UnifiedState) -> dict:
    """
    tool 결과를 반영하여 최종 답변 생성
    """
    question = state["messages"][-1]["content"]
    context = state.get("tool_result") or ""

    prompt = ANSWER_PROMPT.format(
        question=question,
        context=context,
    )

    answer = get_llm_model("gemini").invoke(prompt)

    return {
        "final_answer": answer,
        "messages": state["messages"] + [
            {
                "role": "assistant",
                "content": answer,
            }
        ],
    }
