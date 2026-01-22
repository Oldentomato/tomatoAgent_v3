from fastapi import APIRouter, HTTPException, Request, Depends
from app.services.chat_service import ChatService
from app.schema.chat_model import LLMRequest, LLMResponse, LLMResponseError
from app.src.graph.builder import build_graph

chat_router = APIRouter()
chat_service = ChatService()

def get_neo_db(request: Request):
    return request.app.state.neodb


def get_langgraph():
    graph = build_graph()

    return graph.compile()



# @chat_router.post("/create_chat", response_model=LLMResponse, responses={
#         500: {
#             "description": "요청작업 중 문제 발생",
#             "model": LLMResponseError
#         },
#         502: {
#             "description": "llm요청 중 bad gateway",
#             "model": LLMResponseError
#         }
#     })
# async def create_chat(query: LLMRequest, neo_db=Depends(get_neo_db)):
#     prompt = query.prompt 
#     chat_history = query.chat_history
#     try:
#         await repo.create_conversation(neo_db)
#         return {"status": "ok"}
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=400, detail="User creation failed")


#session_id를 req를 통해 받도록 수정
@chat_router.post("/chat")
async def chat(query: LLMRequest, neo_db=Depends(get_neo_db), langgraph_client=Depends(get_langgraph)):
    # if not await repo.create_branch_message(neo_db, email, password):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    prompt = query.prompt
    session_id = query.session_id
    result = await chat_service.request_llm("", langgraph_client, prompt)
    return {"result": result}
