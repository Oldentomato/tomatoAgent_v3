from app.src.services.embeddings import embeddings

# 예시: 이미 초기화된 vector store가 있다고 가정
# (FAISS, Chroma, Weaviate 등)
from app.src.utils.vectorstore import get_vectorstore


def search(query: str, k: int = 5) -> str:
    """
    내부 코드 / 문서 RAG 검색
    """
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=k)

    if not docs:
        return ""

    return "\n\n".join(
        f"[Document]\n{doc.page_content}"
        for doc in docs
    )
