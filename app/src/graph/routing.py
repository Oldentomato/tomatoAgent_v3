from src.graph.state import State


def route_by_tool_choice(state: State) -> str:
    """
    tool_selector 노드 이후 어떤 노드로 갈지 결정
    """
    return state["tool_choice"]