from app.security.email import make_email_hash

class UserRepository:
    async def get_user_by_provider(
        self,
        conn,
        provider: str,
        provider_id: str 
    ):
        async with conn.transaction():
            return await conn.fetchrow("""
                SELECT id
                FROM users
                WHERE provider = $1
                AND provider_id = $2
            """, provider, provider_id)
    
    async def create_google_user(
        self,
        conn,
        email: str,
        name: str,
        provider_id: str
    ):
        async with conn.transaction():
            return await conn.fetchrow("""
                INSERT INTO users (
                    name,
                    email,
                    provider,
                    provider_id,
                    password_hash
                )
                VALUES (
                    encrypt_text($1),
                    encrypt_text($2),
                    'google',
                    $3,
                    NULL
                )
                RETURNING id
            """,
            name,
            email,
            provider_id
            )


    # async def get_user_by_email_hash(self, conn, email_hash: bytes):
    #     async with conn.transaction():

    #         row = await conn.fetchrow("""
    #             SELECT
    #                 id,
    #                 decrypt_text(email) AS email,
    #                 decrypt_text(name)  AS name,
    #                 created_at
    #             FROM users
    #             WHERE email_hash = $1
    #         """, email_hash)

    #         return dict(row) if row else None


    # async def list_users(self):
    #     conn = await get_connection()

    #     try:
    #         async with conn.transaction():
    #             await init_session(conn)

    #             rows = await conn.fetch("""
    #                 SELECT
    #                     id,
    #                     decrypt_text(email) AS email,
    #                     decrypt_text(name)  AS name,
    #                     created_at
    #                 FROM users
    #                 ORDER BY decrypt_text(name)
    #             """)

    #             return [dict(row) for row in rows]

    #     finally:
    #         await release_connection(conn)

    # async def search_users_by_name(self, keyword: str):
    #     conn = await get_connection()

    #     try:
    #         async with conn.transaction():
    #             await init_session(conn)

    #             rows = await conn.fetch("""
    #                 SELECT
    #                     id,
    #                     decrypt_text(email) AS email,
    #                     decrypt_text(name)  AS name
    #                 FROM users
    #                 WHERE decrypt_text(name) ILIKE $1
    #                 ORDER BY decrypt_text(name)
    #             """, f"%{keyword}%")

    #             return [dict(row) for row in rows]

    #     finally:
    #         await release_connection(conn)

