from app.src.services.embeddings import embeddings
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

import faiss 
import pickle 
import numpy as np

@tool(parse_docstring=True)
def add_content():
    """사용자가 코드 저장을 허용한다면 이 도구를 사용할 것

    Args:
        query (str): 사용자의 질문

    Returns:
        str: JSON 문자열 
    """
    pass 


# api 호출용
def remove_content(user_id: str, content_id: str):
    pass 

# tool node 용
@tool(parse_docstring=True)
def search(query: str, user_id: str, config: RunnableConfig = None, k: int = 5) -> str:
    """저장된 코드를 내부 RAG를 통해 검색

    Args:
        query (str): 사용자의 질문
        user_id (str): 사용자의 id

    Returns:
        str: JSON 문자열 
    """

    rag_minio = config["configurable"]["rag_minio"]
    rag_content_minio = config["configurable"]["rag_content_minio"]
    
    # embedding model load
    try: #minio에 faiss데이터가 없을 경우 faiss를 새로 생성
        minioData = rag_minio.get(user_id)
        embedding_model = pickle.loads(minioData)
        # index = faiss.deserialize_index(embedPickle)
    except Exception as e:
        base_index = faiss.IndexFlatL2(1024)
        embedding_model = faiss.IndexIDMap(base_index)

    # embedding content load
    try:
        userContent = rag_content_minio.get(user_id)
    except Exception as e:
        return f"사용자의 저장된 정보가 없습니다. 에러 메세지: {e}"


    encodeContent = embedding_model.encode(query)
    D, I = embedding_model.search(np.array(encodeContent).reshape(1, -1).astype("float32"), k)

    resultIndex = I[0][0]

    return userContent[str(resultIndex)]['content']

    
