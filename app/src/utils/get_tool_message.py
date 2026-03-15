
def get_tool_from_message(messages):
    # 마지막 assistant 메시지에서 tool call 추출
    last_msg = messages[-1]

    tool_calls = last_msg.get("tool_calls", [])

    if not tool_calls:
        return None

    # 첫 번째 tool call 사용
    tool_call = tool_calls[0]

    query = tool_call["args"].get("query")

    if not query:
        return None

    return query