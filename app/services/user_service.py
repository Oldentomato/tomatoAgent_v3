from app.repository.user_repository import UserRepository
from app.auth.google import verify_google_token, get_google_auth_url, google_redirect
from util.gen_id import generate_id
from app.core.exception import Unauthorized, BadRequest


class UserService:

    def __init__(self):
        self.user_repo = UserRepository()


    async def google_token_service(self):
        auth_url = get_google_auth_url()
        if not auth_url:
            raise BadRequest()
        
        return auth_url
    
    async def google_redirect_service(self, code):
        credential = google_redirect(code=code)
        if not credential:
            raise BadRequest()
        
        return credential

    async def check_user_redis(self, req, session_id):
        # 우선 redis에서 유저가 있는지 체크하는 함수
        pass
    
    async def google_login_service(self, req, db, id_token: str):
        user_info = verify_google_token(id_token)
        if not user_info:
            raise Unauthorized()
        

        user = await self.user_repo.get_user_by_provider(
            db,
            provider="google",
            provider_id=user_info["provider_id"]
        )

        if not user:
            user = await self.user_repo.create_google_user(
                db,
                email=user_info["email"],
                name=user_info["name"],
                provider_id=user_info["provider_id"]
            )

        session_id = generate_id()
        await req.app.state.redis_user_session.set(session_id, {
            "user_id": user["id"]
            # 여러 정보 더 넣어야함
        })
        return session_id