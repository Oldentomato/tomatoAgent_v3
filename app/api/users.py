from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.responses import RedirectResponse
from app.services.user_service import UserService
from app.db.postdb_pool import get_postdb_conn
from app.schema.user_model import GoogleLoginRequest, GoogleLoginResponse, UserLoginResponse, UserResponseError
from app.core.exception import GoogleCodeMissError

user_router = APIRouter()
user_service = UserService()


@user_router.post("/auth/google/login", response_model=GoogleLoginResponse, responses={
        400: {
            "description": "잘못된 요청",
            "model": UserResponseError
        },
        401: {
            "description": "구글 인증 실패",
            "model": UserResponseError
        },
        500: {
            "description": "서버 내부 오류",
            "model": UserResponseError
        }
    })
async def google_login(req: GoogleLoginRequest, res: Response, conn=Depends(get_postdb_conn)):
    session_id = await user_service.google_login_service(conn, req.id_token)

    res.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,   # HTTPS 환경
        samesite="lax"
    )

    return {
        "status": "ok",
        "success": True,
        "status_code": 200
    }

@user_router.get("/auth/google/url")
async def get_google_token():
    auth_url = await user_service.google_token_service()

    return RedirectResponse(auth_url)

@user_router.get("/api/callback/auth/google")
async def get_google_token(req: Request):
    code = req.query_params.get("code")
    # state = req.query_params.get("state")

    if not code:
        raise GoogleCodeMissError()
    
    credentials  = await user_service.google_redirect_service(code)

    return {
        "success": True,
        "status_code": 200,
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "id_token": credentials.id_token,
    }

