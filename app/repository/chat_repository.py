from app.db.neodb_pool import get_session, release_session
from util.gen_id import generate_id

class ChatRepository:
    async def create_conversation(self, db, title):
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                async with session.begin_transaction() as tx:
                    conv_id = generate_id()
                    tx.run(
                        """
                        CREATE (c:Conversation {
                            id: $id,
                            title: $title,
                            created_at: datetime()
                        })
                        """,
                        id=conv_id,
                        title=title
                    )
                    await tx.commit()
                    return conv_id
        except Exception:
            raise

        finally:
            await release_session(driver)
        

    async def create_root_message(self, db, conversation_id, role, content):
        """루트 메시지 생성 (parent 없음)"""
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                async with session.begin_transaction() as tx:
                    msg_id = generate_id()
                    with driver.session() as session:
                        tx.run(
                            """
                            MATCH (c:Conversation {id: $cid})
                            CREATE (m:Message {
                                id: $mid,
                                role: $role,
                                content: $content,
                                created_at: datetime()
                            })
                            CREATE (c)-[:HAS_MESSAGE]->(m)
                            """,
                            cid=conversation_id,
                            mid=msg_id,
                            role=role,
                            content=content
                        )
                        await tx.commit()
                        return msg_id
                
        except Exception:
            raise

        finally:
            await release_session(driver)


    async def create_branch_message(self, db, conversation_id, parent_message_id, role, content):
        """분기 메시지 생성"""
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                async with session.begin_transaction() as tx:
                    msg_id = generate_id()
                    session.run(
                        """
                        MATCH (c:Conversation {id: $cid})
                        MATCH (p:Message {id: $pid})
                        CREATE (m:Message {
                            id: $mid,
                            role: $role,
                            content: $content,
                            created_at: datetime()
                        })
                        CREATE (c)-[:HAS_MESSAGE]->(m)
                        CREATE (p)-[:NEXT]->(m)
                        """,
                        cid=conversation_id,
                        pid=parent_message_id,
                        mid=msg_id,
                        role=role,
                        content=content
                    )
                    await tx.commit()
                    return msg_id
        except Exception:
            raise

        finally:
            await release_session(driver)


    async def get_context_until_leaf(self, db, leaf_message_id):
        """특정 분기 전체 조회 (leaf 기준)"""
        driver = await get_session(db)

        try:
            async with driver.session() as session:
                async with session.begin_transaction() as tx:
                    result = tx.run(
                        """
                        MATCH path = (root:Message)-[:NEXT*]->(leaf:Message {id: $leaf_id})
                        WHERE NOT ()-[:NEXT]->(root)
                        RETURN nodes(path) AS messages
                        """,
                        leaf_id=leaf_message_id
                    )

                    record = result.single()
                    messages = record["messages"]

                    return [
                        {
                            "role": m["role"],
                            "content": m["content"]
                        }
                        for m in messages
                    ]
                
        except Exception:
            raise

        finally:
            await release_session(driver)