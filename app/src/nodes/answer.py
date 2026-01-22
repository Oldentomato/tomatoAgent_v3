from graph.state import State
from src.services.llm import llm
from src.utils.prompts import load_prompt


ANSWER_PROMPT = load_prompt("answer.md")


async def answer_node(state: State) -> dict:
    """
    tool 결과를 반영하여 최종 답변 생성
    """
    question = state["messages"][-1]["content"]
    context = state.get("tool_result") or ""

    prompt = ANSWER_PROMPT.format(
        question=question,
        context=context,
    )

    answer = llm.invoke(prompt)

    return {
        "final_answer": answer,
        "messages": state["messages"] + [
            {
                "role": "assistant",
                "content": answer,
            }
        ],
    }
