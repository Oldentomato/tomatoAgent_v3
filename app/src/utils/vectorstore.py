_vectorstore = None


def get_vectorstore():
    global _vectorstore

    if _vectorstore is None:
        # TODO: 실제 vectorstore 초기화
        # 예: FAISS.load_local(...)
        raise NotImplementedError("VectorStore not initialized")

    return _vectorstore
