from botocore.exceptions import ClientError
import pickle
from app.minio.keys import user_content
import faiss

class BaseSessionStore:
    def __init__(self, s3_client, bucket_name, category):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.category = category

    def get(self, user_id: str):
        file_key = user_content(user_id, self.category)
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except ClientError:
            raise Exception(f"{file_key} does not exist")


    def put(self, user_id: str, content):
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=user_content(user_id, self.category),
            Body=content
        )

    def delete(self, user_id: str):
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=user_content(user_id, self.category)
        )
          

class RAGSessionStore(BaseSessionStore):
    def __init__(self, s3_client):
        super().__init__(s3_client, "codearchive", "model")

    def get(self, user_id: str, dim: int):
        file_key = user_content(user_id, self.category)
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return pickle.loads(response['Body'].read())
        except:#user_id가 없을경우
            base_index = faiss.IndexFlatL2(dim)
            return faiss.IndexIDMap(base_index)


class ContentSessionStore(BaseSessionStore):
    def __init__(self, s3_client):
        super().__init__(s3_client, "codearchive", "content")

    def get(self, user_id: str):
        file_key = user_content(user_id, self.category)
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except:#user_id가 없을경우
            return {}