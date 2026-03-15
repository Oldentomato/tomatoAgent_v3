from botocore.exceptions import ClientError
import pickle
from app.minio.keys import user_content

class BaseSessionStore:
    def __init__(self, s3_client, bucket_name, category):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.category = category

    async def get(self, user_id: str):
        file_key = user_content(user_id, self.category)
        try:
            await self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            response = await self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return await response['Body'].read()
        except ClientError:
            raise Exception(f"{file_key} does not exist")

    async def put(self, user_id: str, content):
        await self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=user_content(user_id, self.category),
            Body=content
        )

    async def delete(self, user_id: str):
        await self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=user_content(user_id, self.category)
        )
          

class RAGSessionStore(BaseSessionStore):
    def __init__(self, s3_client):
        super().__init__(s3_client, "codeArchive", "model")


class ContentSessionStore(BaseSessionStore):
    def __init__(self, s3_client):
        super().__init__(s3_client, "chatArchive", "content")