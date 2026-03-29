import asyncio
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from util.gen_id import generate_id

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
from ag_ui.encoder import EventEncoder  # Encoder for converting events to SSE format
from copilotkit import CopilotKitState  # Base state class from CopilotKit
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent


from app.services.chat_service import ChatService
from app.repository.chat_repository import ChatRepository
from app.src.graphs.codeArchive.state import UnifiedState
from app.db.neodb_pool import get_session
from app.db.minio_client import get_rag_minio, get_content_minio

chat_router = APIRouter()
chat_service = ChatService()


def get_code_archive_graph(request: Request):
    return request.app.state.code_archive_graph


def get_code_ingest_graph(request: Request):
    return request.app.state.code_ingest_graph



@chat_router.post("/langgraph-agent")
async def langgraph_agent_endpoint(input_data: RunAgentInput, request: Request, neo_db=Depends(get_session), rag_minio=Depends(get_rag_minio), content_minio=Depends(get_content_minio),  code_archive_graph=Depends(get_code_archive_graph)):
    
    chat_repo = ChatRepository()
    
    agent=LangGraphAGUIAgent( #추후에 얘를 request.app 으로 지정할것
        name="codeArchive",
        description="코드를 분석하여 저장하거나, 검색할 수 있는 에이전트입니다.",
        graph=code_archive_graph,
        config={
            "configurable": {"thread_id": input_data.thread_id,
                            "neo_db": neo_db,
                            "chat_repo": chat_repo,
                            "minio_client": rag_minio,
                            "rag_content_minio": content_minio}
        }
    )

    
    # Get the accept header from the request
    accept_header = request.headers.get("accept")

    # Create an event encoder to properly format SSE events
    encoder = EventEncoder(accept=accept_header)

    async def event_generator():
        async for event in agent.run(input_data):
            yield encoder.encode(event)

    return StreamingResponse(
        event_generator(),
        media_type=encoder.get_content_type()
    )

@chat_router.get("/langgraph-agent/health")
def health(code_archive_graph=Depends(get_code_archive_graph)):
    """Health check."""
    agent=LangGraphAGUIAgent(
        name="codeArchive",
        description="코드를 분석하여 저장하거나, 검색할 수 있는 에이전트입니다.",
        graph=code_archive_graph,
    ),
    return {
        "status": "ok",
        "agent": {
            "name": agent.name,
        }
    }


# add_langgraph_fastapi_endpoint(
#   app=chat_router,
#   agent=LangGraphAGUIAgent(
#     name="sample_agent",
#     description="An example agent to use as a starting point for your own agent.",
#     graph=get_code_archive_graph,
#   ),
#   path="/",
# )

# class AgentState(CopilotKitState):
#     """
#     AgentState defines the structure of data that flows through the agent.
#     It extends CopilotKitState and contains all the information needed
#     for stock analysis and investment operations.
#     """
    
#     # List of available tools for the agent to use
#     tools: list
#     # Conversation history between user and assistant
#     messages: list

#     # Log of tool executions and their results
#     tool_logs: list

# # FastAPI endpoint that handles agent execution requests
# @chat_router.post("/langgraph-agent")
# async def langgraph_agent(request: Request, input_data: RunAgentInput, neo_db=Depends(get_session), rag_minio=Depends(get_rag_minio), content_minio=Depends(get_content_minio),  code_archive_graph=Depends(get_code_archive_graph)):
#     """
#     Main endpoint that processes agent requests and streams back events.
    
#     Args:
#         input_data (RunAgentInput): Contains thread_id, run_id, messages, tools, and state
        
#     Returns:
#         StreamingResponse: Server-sent events stream with agent execution updates
#     """
#     try:

#         # Define async generator function to produce server-sent events
#         async def event_generator():
#             # Step 1: Initialize event encoding and communication infrastructure
#             encoder = EventEncoder()  # Converts events to SSE format
#             event_queue = asyncio.Queue()  # Queue for events from agent execution

#             # Helper function to add events to the queue
#             def emit_event(event):
#                 event_queue.put_nowait(event)

#             # Generate unique identifier for this message thread
#             message_id = generate_id()

#             # Step 2: Signal the start of agent execution
#             yield encoder.encode(
#                 RunStartedEvent(
#                     type=EventType.RUN_STARTED,
#                     thread_id=input_data.thread_id,
#                     run_id=input_data.run_id,
#                 )
#             )



#             # try:
#             #     user_id = request.state.user_info.user_id
#             # except:
#             #     raise
            
#             # Step 4: Initialize agent state with input data
#             state = UnifiedState(
#                 tools=input_data.tools,
#                 messages=input_data.messages,
#                 code= "",
#                 user_id="aaaa", #user_id 
#                 file_path= "",
#                 language= "",
#                 auto_summary= "",
#                 final_summary= "",
#                 should_save= True,
#                 tool_logs= []
#             )

#             # Step 3: Send initial state snapshot to frontend
#             yield encoder.encode(
#                 StateSnapshotEvent(
#                     type=EventType.STATE_SNAPSHOT, 
#                     snapshot={
#                         "messages": state["messages"],
#                         "auto_summary": state["auto_summary"],
#                         "final_summary": state["final_summary"],
#                         "tool_logs": []
#                     }
#                 )
#             )
            
#             # Step 5: Create and configure the LangGraph agent
#             agent = code_archive_graph

#             chat_repo = ChatRepository()


#             # Step 6: Start agent execution asynchronously
#             agent_task = asyncio.create_task(
#                 agent.ainvoke(
#                     state, config={
#                         "emit_event": emit_event, 
#                         "message_id": message_id, 
#                         "configurable": {"thread_id": input_data.thread_id,
#                                         "neo_db": neo_db,
#                                         "chat_repo": chat_repo,
#                                         "minio_client": rag_minio,
#                                         "rag_content_minio": content_minio}}
#                 )
#             )
            
#             # Step 7: Stream events from agent execution as they occur
#             while True:
#                 try:
#                     # Wait for events with short timeout to check if agent is done
#                     event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
#                     yield encoder.encode(event)
#                 except asyncio.TimeoutError:
#                     # Check if the agent execution has completed
#                     if agent_task.done():
#                         result = await agent_task
#                         print("FINAL STATE:", result)
#                         break

#             # Step 8: Clear tool logs after execution
#             yield encoder.encode(
#                 StateDeltaEvent(
#                     type=EventType.STATE_DELTA,
#                     delta=[
#                         {
#                             "op": "replace",
#                             "path": "/tool_logs",
#                             "value": []
#                         }
#                     ]
#                 )
#             )
#             # Step 9: Handle the final message from the agent
#             if state["messages"][-1].role == "assistant":
#                 # Check if the assistant made tool calls
#                 if state["messages"][-1].tool_calls:
#                     # Step 9a: Stream tool call events if tools were used
                    
#                     # Signal the start of tool execution
#                     yield encoder.encode(
#                         ToolCallStartEvent(
#                             type=EventType.TOOL_CALL_START,
#                             tool_call_id=state["messages"][-1].tool_calls[0].id,
#                             toolCallName=state["messages"][-1]
#                             .tool_calls[0]
#                             .function.name,
#                         )
#                     )

#                     # Send the tool call arguments
#                     yield encoder.encode(
#                         ToolCallArgsEvent(
#                             type=EventType.TOOL_CALL_ARGS,
#                             tool_call_id=state["messages"][-1].tool_calls[0].id,
#                             delta=state["messages"][-1]
#                             .tool_calls[0]
#                             .function.arguments,
#                         )
#                     )

#                     # Signal the end of tool execution
#                     yield encoder.encode(
#                         ToolCallEndEvent(
#                             type=EventType.TOOL_CALL_END,
#                             tool_call_id=state["messages"][-1].tool_calls[0].id,
#                         )
#                     )
#                 else:
#                     # Step 9b: Stream text message if no tools were used
                    
#                     # Signal the start of text message
#                     yield encoder.encode(
#                         TextMessageStartEvent(
#                             type=EventType.TEXT_MESSAGE_START,
#                             message_id=message_id,
#                             role="assistant",
#                         )
#                     )

#                     # Stream the message content in chunks for better UX
#                     if state["messages"][-1].content:
#                         content = state["messages"][-1].content
                        
#                         # Split content into 5 parts for gradual streaming
#                         n_parts = 5
#                         part_length = max(1, len(content) // n_parts)
#                         parts = [content[i:i+part_length] for i in range(0, len(content), part_length)]
                        
#                         # Handle rounding by merging extra parts into the last one
#                         if len(parts) > n_parts:
#                             parts = parts[:n_parts-1] + [''.join(parts[n_parts-1:])]
                        
#                         # Stream each part with a delay for typing effect
#                         for part in parts:
#                             yield encoder.encode(
#                                 TextMessageContentEvent(
#                                     type=EventType.TEXT_MESSAGE_CONTENT,
#                                     message_id=message_id,
#                                     delta=part,
#                                 )
#                             )
#                             await asyncio.sleep(0.5)  # 500ms delay between chunks
#                     else:
#                         # Send error message if content is empty
#                         yield encoder.encode(
#                             TextMessageContentEvent(
#                                 type=EventType.TEXT_MESSAGE_CONTENT,
#                                 message_id=message_id,
#                                 delta="Something went wrong! Please try again.",
#                             )
#                         )
                    
#                     # Signal the end of text message
#                     yield encoder.encode(
#                         TextMessageEndEvent(
#                             type=EventType.TEXT_MESSAGE_END,
#                             message_id=message_id,
#                         )
#                     )

#             # Step 10: Signal the completion of the entire agent run
#             yield encoder.encode(
#                 RunFinishedEvent(
#                     type=EventType.RUN_FINISHED,
#                     thread_id=input_data.thread_id,
#                     run_id=input_data.run_id,
#                 )
#             )

#     except Exception as e:
#         # Log any errors that occur during execution
#         print(e)

#     # Return the event generator as a streaming response
#     return StreamingResponse(event_generator(), media_type="text/event-stream")


# # ag_ui용 커스텀 엔드포인트 - db/minio 의존성 주입
# @chat_router.post("/code-ingest")
# async def code_ingest_endpoint(input_data: RunAgentInput, request: Request):
#     """
#     코드 인제스트를 위한 AG-UI 엔드포인트
#     Request에서 rag_minio를 가져와서 state에 주입합니다.
#     """
#     # Request에서 의존성 가져오기
#     rag_minio = request.app.state.rag_minio
    
#     # input_data.state에 의존성 추가
#     if input_data.state is None:
#         input_data.state = {}
    
#     input_data.state["rag_minio"] = rag_minio
    
#     # agent 생성
#     agent = LangGraphAGUIAgent(
#         name="code_ingest_agent",
#         description="코드의 내용을 요약하고 코드와 요약된 내용을 저장합니다.",
#         graph=code_ingest_build_graph(),
#     )
    
#     # endpoint.py와 동일한 로직
#     accept_header = request.headers.get("accept")
#     encoder = EventEncoder(accept=accept_header)

#     conversation_id = (
#         request.headers.get("x-copilotkit-conversation-id")
#         or input_data.state.get("conversationId")
#     )
    
#     async def event_generator():
#         async for event in agent.run(
#             input_data,
#             config={"configurable": {"thread_id": conversation_id}}
#         ):
#             yield encoder.encode(event)
    
#     return StreamingResponse(
#         event_generator(),
#         media_type=encoder.get_content_type()
#     )


# @chat_router.get("/code-ingest/health")
# def code_ingest_health():
#     """Health check endpoint for code-ingest agent."""
#     return {
#         "status": "ok",
#         "agent": {
#             "name": "code_ingest_agent",
#         }
#     }




#session_id를 req를 통해 받도록 수정
# @chat_router.post("/chat")
# async def chat(request: LLMRequest, code_archive_graph=Depends(get_code_archive_graph), neo_db=Depends(get_session), rag_minio=Depends(get_minio)):
#     # if not await repo.create_branch_message(neo_db, email, password):
#     #     raise HTTPException(status_code=401, detail="Invalid credentials")

#     prompt = request.prompt
#     # session_id = query.session_id
#     result = await chat_service.request_llm(rag_minio, neo_db, "", code_archive_graph, prompt)
#     return {"result": result}


