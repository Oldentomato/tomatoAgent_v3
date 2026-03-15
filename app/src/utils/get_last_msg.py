def extract_last_user_message(messages):
    for m in reversed(messages):
        role = getattr(m, "role", None)
        content = getattr(m, "content", "")

        if role == "user" and content.strip():
            return content

    return None