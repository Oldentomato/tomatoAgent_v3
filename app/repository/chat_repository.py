from app.db.neodb_pool import get_session, release_session
from util.gen_id import generate_id

class ChatRepository:
    async def ensure_conversation(self, db, conversation_id: str, title: str = "New Chat"):
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                await session.run(
                    """
                    MERGE (c:Conversation {id: $id})
                    ON CREATE SET
                        c.title = $title,
                        c.created_at = datetime()
                    """,
                    id=conversation_id,
                    title=title
                )
        finally:
            await release_session(driver)
        

    async def create_turn(
        self,
        db,
        conversation_id: str,
        user_content: str,
        assistant_content: str
    ):
        """
        하나의 Turn 생성
        (user + tool retry + final answer 결과)
        """
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                turn_id = generate_id()

                await session.run(
                    """
                    MATCH (c:Conversation {id: $cid})

                    OPTIONAL MATCH (c)-[:HAS_TURN]->(last:Turn)
                    WITH c, last
                    ORDER BY last.index DESC
                    LIMIT 1

                    CREATE (t:Turn {
                        id: $tid,
                        index: coalesce(last.index, -1) + 1,
                        user_content: $user_content,
                        assistant_content: $assistant_content,
                        created_at: datetime()
                    })

                    CREATE (c)-[:HAS_TURN]->(t)

                    FOREACH (_ IN CASE WHEN last IS NOT NULL THEN [1] ELSE [] END |
                        CREATE (last)-[:NEXT]->(t)
                    )
                    """,
                    cid=conversation_id,
                    tid=turn_id,
                    user_content=user_content,
                    assistant_content=assistant_content
                )

                return turn_id
        finally:
            await release_session(driver)


    async def add_tool_call(
        self,
        db,
        turn_id: str,
        name: str,
        tool_input: str,
        tool_output: str,
        order: int
    ):
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                tool_id = generate_id()

                await session.run(
                    """
                    MATCH (t:Turn {id: $tid})
                    CREATE (tc:ToolCall {
                        id: $id,
                        name: $name,
                        input: $input,
                        output: $output,
                        order: $order
                    })
                    CREATE (t)-[:HAS_TOOL_CALL]->(tc)
                    """,
                    tid=turn_id,
                    id=tool_id,
                    name=name,
                    input=tool_input,
                    output=tool_output,
                    order=order
                )

                return tool_id
        finally:
            await release_session(driver)

    async def get_chat_context(
        self,
        db,
        conversation_id: str,
        limit: int = 10
    ):
        """
        LangGraph에 넘길 context 생성
        (최근 N턴)
        """
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                result = await session.run(
                    """
                    MATCH (c:Conversation {id: $cid})-[:HAS_TURN]->(t:Turn)
                    RETURN t
                    ORDER BY t.index DESC
                    LIMIT $limit
                    """,
                    cid=conversation_id,
                    limit=limit
                )

                turns = [r["t"] async for r in result]
                turns.reverse()

                messages = []
                for t in turns:
                    messages.append({
                        "role": "user",
                        "content": t["user_content"]
                    })
                    messages.append({
                        "role": "assistant",
                        "content": t["assistant_content"]
                    })

                return messages
        finally:
            await release_session(driver)


    async def get_chat_list(self, db):
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                result = await session.run(
                    """
                    MATCH (c:Conversation)-[:HAS_TURN]->(t:Turn)
                    WITH c, t
                    ORDER BY t.index DESC
                    WITH c, collect(t)[0] AS last_turn
                    RETURN
                        c.id AS conversation_id,
                        c.title AS title,
                        last_turn.user_content AS last_question,
                        last_turn.created_at AS updated_at
                    ORDER BY updated_at DESC
                    """
                )

                return [
                    {
                        "conversation_id": r["conversation_id"],
                        "title": r["title"],
                        "last_question": r["last_question"],
                        "updated_at": r["updated_at"]
                    }
                    async for r in result
                ]
        finally:
            await release_session(driver)