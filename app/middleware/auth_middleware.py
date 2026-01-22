from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
from config.settings import VERIFY_PASS_URLS
from app.core.exception import InvalidCookieError, InvalidSessionError, MiddlewareInternalError

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 인증이 필요없는 엔드포인트일 경우 패스
        if request.url.path in VERIFY_PASS_URLS:
            return await call_next(request)

        try:
            # 예시: Authorization 헤더에서 토큰 추출
            # auth_header = request.headers.get("Authorization")
            # if auth_header:
            #     session_id = auth_header.replace("Bearer ", "")

            session_id = request.cookies.get("session_id")
            if session_id:
                # Redis에서 토큰 검증
                user_info = await request.app.state.redis_user_session.get(session_id)
                if not user_info:
                    raise InvalidSessionError()

                # request.state에 사용자 정보 저장
                request.state.user_info = user_info
                # request.app.state = fastAPI 앱 전체에 할당
                # request.state = 각 요청마다 할당
            else:
                raise InvalidCookieError()

            response = await call_next(request)

        except Exception:
            raise MiddlewareInternalError()

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response