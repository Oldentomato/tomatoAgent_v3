from langgraph.types import interrupt
from app.src.graph.state import UnifiedState
import uuid  # For generating unique message IDs

import asyncio  # For asynchronous programming

# Import AG UI core components for event-driven communication
from ag_ui.core import (
    RunAgentInput,        # Input data structure for agent runs
    StateSnapshotEvent,   # Event for capturing state snapshots
    EventType,            # Enumeration of all event types
    RunStartedEvent,      # Event to signal run start
    RunFinishedEvent,     # Event to signal run completion
    TextMessageStartEvent,    # Event to start text message streaming
    TextMessageEndEvent,      # Event to end text message streaming
    TextMessageContentEvent,  # Event for text message content chunks
    ToolCallStartEvent,       # Event to start tool call
    ToolCallEndEvent,         # Event to end tool call
    ToolCallArgsEvent,        # Event for tool call arguments
    StateDeltaEvent           # Event for state changes
)



async def ask_search_method_node(state: UnifiedState, config):
    # choice = interrupt({
    #     "type": "search_method",
    #     "message": "검색 방법을 선택해주세요",
    #     "options": ["rag", "web", "cancel"]
    # })

    # return {"search_choice": choice}
    # Step 16: Add assistant message with chart rendering tool call
    # state["messages"].append(
    #     AssistantMessage(
    #         role="assistant",
    #         tool_calls=[
    #             {
    #                 "id": str(uuid.uuid4()),
    #                 "type";: "function",
    #                 "function": {
    #                     "name": "render_standard_charts_and_table",
    #                     "arguments": json.dumps(
    #                         {"investment_summary": state["investment_summary"]}
    #                     ),
    #                 },
    #             }
    #         ],
    #         id=str(uuid.uuid4()),
    #     )
    # )

    # # Step 17: Update tool log status to completed
    # index = len(state["tool_logs"]) - 1
    # config.get("configurable").get("emit_event")(
    #     StateDeltaEvent(
    #         type=EventType.STATE_DELTA,
    #         delta=[
    #             {
    #                 "op": "replace",
    #                 "path": f"/tool_logs/{index}/status",
    #                 "value": "completed"
    #             }
    #         ],
    #     )
    # )
    # await asyncio.sleep(0)

    # # Step 18: Direct workflow to the insights generation node
    # return Command(goto="ui_decision", update=state)
    pass