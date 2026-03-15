from app.src.graph.state import UnifiedState

def route_by_search_choice(state: UnifiedState):
    if state["search_choice"] == "rag":
        return "rag"
    elif state["search_choice"] == "web":
        return "web"
    else:
        return "end"