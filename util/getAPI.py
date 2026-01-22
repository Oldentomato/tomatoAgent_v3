from dotenv import load_dotenv
import os

# 환경 값 가져오기 (k8s에서는 이미 ENV 변수 주입됨)

load_dotenv(dotenv_path=".env", override=True, verbose=True)
# prod 환경: K8s Secret을 통해 이미 환경 변수가 주입되므로 .env 로드 X


def getApiKey(apiName: str):
    key = os.getenv(apiName)
    if key is None:
        raise Exception(f"No Api Key: {apiName}")
    return key