from app.repository.chat_repository import ChatRepository
from app.core.exception import Unauthorized, BadRequest


class ChatService:

    def __init__(self):
        self.chat_repo = ChatRepository()

    async def __get_initial_state(
        self,
        rag_minio,
        db,
        conversation_id: str,
        query: str
    ):
        """
        기존 Turn 기반 context + 현재 user query
        """
        # node상에 메세지 db 불러오는걸 구현해서 필요없을 수 있음
        messages = await self.chat_repo.get_chat_context(
            db=db,
            conversation_id=conversation_id,
            limit=10
        )

        messages.append({
            "role": "user",
            "content": query
        })

        return {
            "messages": messages,
            "tool_choice": "none",
            "user_id": "",
            "rag_minio": rag_minio,
            "tool_input": None,
            "tool_result": None,
            "rag_success": None,
            "final_answer": None,
        }

    async def request_llm(
        self,
        rag_minio,
        db,
        conversation_id: str,
        graph,
        query: str
    ):
        """
        LangGraph 실행 + Turn 저장
        """
        try:
            # 1. LangGraph initial state 구성
            state = await self.__get_initial_state(
                rag_minio=rag_minio,
                db=db,
                conversation_id=conversation_id,
                query=query
            )

            # 2. LangGraph 실행
            result = await graph.ainvoke(
                state,
                config={
                    "configurable": {
                        "thread_id": conversation_id
                    }
                }
            )

            final_answer = result["final_answer"]

            # 3. Turn 저장 (user + final answer)
            await self.chat_repo.create_turn(
                db=db,
                conversation_id=conversation_id,
                user_content=query,
                assistant_content=final_answer
            )

            return final_answer

        except Exception:
            raise BadRequest()

    async def get_chat_history(
        self,
        db,
        conversation_id: str,
        limit: int = 20
    ):
        """
        UI용 전체 대화 히스토리 (Turn 단위)
        """
        return await self.chat_repo.get_chat_context(
            db=db,
            conversation_id=conversation_id,
            limit=limit
        )

    async def get_chat_list(self, db):
        """
        채팅 목록 조회
        """
        return await self.chat_repo.get_chat_list(db)

    async def __get_rag_origin_data(self, db, user_id):
        """
        rag의 원본 데이터 정보(embedding 전 데이터) 가져오기
        """
        pass

    async def add_rag_content(self, minio_db, content):
        """
        rag content 추가 요청
        """
        pass 