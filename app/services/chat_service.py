from app.repository.chat_repository import ChatRepository
from app.redis.session_store import UserSessionStore
from app.db.redis_client import get_redis
from app.core.exception import Unauthorized, BadRequest


class ChatService:

    def __init__(self):
        self.chat_repo = ChatRepository()
        self.redis_session = UserSessionStore(get_redis()) 

    def __get_initial_state(self, query):
        return {
            "messages": [{"role": "user", "content": query}],
            "tool_choice": "none",
            "tool_input": None,
            "tool_result": None,
            "rag_success": None,
            "final_answer": None,
        }

    async def request_llm(self, session_id, graph, query): 
        state = self.__get_initial_state(query)

        result = await graph.ainvoke(state,
                                    config={
                                        "configurable": {
                                            "thread_id": session_id
                                        }}
                                    )

        return result["final_answer"]
    
    async def get_chat_history(self):
        pass 


    async def get_chat_list(self):
        pass