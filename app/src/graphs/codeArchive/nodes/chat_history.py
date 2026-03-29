from app.src.graphs.codeArchive.state import UnifiedState

async def load_chat_history(state: UnifiedState, config):
    """
    그래프 시작 시 호출 — Neo4j에서 최근 대화 로드
    """
    chat_repo = config["configurable"]["chat_repo"]
    db = config["configurable"]["neo_db"]
    conversation_id = config["configurable"]["thread_id"]

    """
    MERGE를 이용하여
    없으면 생성
    있으면 그대로 사용
    """
    await chat_repo.ensure_conversation(db, conversation_id)

    messages = await chat_repo.get_chat_context(
        db,
        conversation_id,
        limit=10
    )

    existing = state.get("messages", [])

    return {
        **state,
        "messages": messages + existing
    }


async def persist_chat_turn(state: UnifiedState, config):
    """
    한 turn 저장
    (마지막 assistant 응답 기준)
    """
    chat_repo = config["configurable"]["chat_repo"]
    db = config["configurable"]["neo_db"]
    conversation_id = config["configurable"]["thread_id"]

    messages = state.get("messages", [])

    if not messages:
        return state

    # 마지막 assistant 찾기
    last_assistant_idx = None
    for i in reversed(range(len(messages))):
        if messages[i]["role"] == "assistant":
            last_assistant_idx = i
            break

    if last_assistant_idx is None:
        return state

    # 그 앞의 user 찾기
    last_user_idx = None
    for i in reversed(range(last_assistant_idx)):
        if messages[i]["role"] == "user":
            last_user_idx = i
            break

    if last_user_idx is None:
        return state

    user_msg = messages[last_user_idx]
    assistant_msg = messages[last_assistant_idx]

    await chat_repo.create_turn(
        db,
        conversation_id=conversation_id,
        user_content=user_msg["content"],
        assistant_content=assistant_msg["content"]
    )

    return state