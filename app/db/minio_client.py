import boto3
from botocore.client import Config
from fastapi import Request
from app.minio.session_store import RAGSessionStore, ContentSessionStore
from config.settings import MINIO_S3, MINIO_USER, MINIO_PASSWORD


def init_minio(app):
    # S3 클라이언트 생성
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_S3,           # MinIO 서버 URL
        aws_access_key_id=MINIO_USER,          # 인증 정보
        aws_secret_access_key=MINIO_PASSWORD,
        config=Config(signature_version='s3v4')  # S3 API 버전
    )

    app.state.rag_minio = RAGSessionStore(s3_client)
    app.state.content_minio = ContentSessionStore(s3_client)


def get_rag_minio(request: Request):
    minio_client = request.app.state.rag_minio

    if minio_client is None:
        raise RuntimeError("Minio not initialized")
    return minio_client

def get_content_minio(request: Request):
    minio_client = request.app.state.content_minio 

    if minio_client is None:
        raise RuntimeError("Minio not initialized")

    return minio_client