# auth/google.py
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
from config.settings import GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URL
from config.google_config import CLIENT_CONFIG, SCOPES

def verify_google_token(token: str) -> dict:
    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        return {
            "email": payload["email"],
            "name": payload.get("name", ""),
            "provider_id": payload["sub"]
        }
    except Exception:
        return None

def get_google_auth_url() -> str:
    try:
        flow = Flow.from_client_config(CLIENT_CONFIG, SCOPES, redirect_uri = GOOGLE_REDIRECT_URL)

        auth_url, _ = flow.authorization_url(
            access_type="offline", # refresh_token을 받기 위한 옵션
            include_granted_scopes="true", #이미 승인된 scope를 유지하면서 추가 scope만 요청(Google 권장 옵션)
            # prompt="consent" # 사용자가 로그인할 때마다 동의 화면 강제 표시(개발용)
        )


        return auth_url
    
    except Exception:
        return None
    
def google_redirect(code: str) -> str:
    try:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URL,
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        return credentials
    
    except Exception:
        return None