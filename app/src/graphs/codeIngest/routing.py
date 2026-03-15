from app.src.graphs.codeIngest.state import CodeIngestState


def route_by_save_choice(state: CodeIngestState) -> str:
    """
    should_save 값에 따라 다음 노드 선택
    - True  → "save_to_faiss"
    - False → "end"
    """
    return "save_to_faiss" if state.get("should_save") else "end"