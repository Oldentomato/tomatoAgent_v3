from util.gen_id import generate_id
from ag_ui.core import StateDeltaEvent, EventType


def start_tool_log(state, config, message: str):
    tool_log_id = generate_id()

    if "tool_logs" not in state:
        state["tool_logs"] = []

    state["tool_logs"].append({
        "id": tool_log_id,
        "message": message,
        "status": "processing"
    })

    emit = config.get("configurable").get("emit_event")

    emit(
        StateDeltaEvent(
            type=EventType.STATE_DELTA,
            delta=[
                {
                    "op": "add",
                    "path": "/tool_logs/-",
                    "value": {
                        "id": tool_log_id,
                        "message": message,
                        "status": "processing"
                    }
                }
            ],
        )
    )

    return tool_log_id


def complete_tool_log(state, config):
    emit = config.get("configurable").get("emit_event")


    index = len(state["tool_logs"]) - 1


    emit(
        StateDeltaEvent(
            type=EventType.STATE_DELTA,
            delta=[
                {
                    "op": "replace",
                    "path": f"/tool_logs/{index}/status",
                    "value": "completed"
                }
            ],
        )
    )