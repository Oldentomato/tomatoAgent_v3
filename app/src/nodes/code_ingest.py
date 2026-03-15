from typing import Dict, Any
import pickle
import faiss
import asyncio
import numpy as np

from langgraph.types import interrupt

from app.src.graph.state import UnifiedState
from app.src.services.llm import get_llm_model
from app.src.services.embeddings import embeddings
from app.src.tools.rag_search import get_faiss_or_pickle
from app.src.utils.tool_logs import complete_tool_log, start_tool_log


async def generate_code_summary_node(state: UnifiedState, config) -> Dict[str, Any]:
    """
    1단계: 코드에 대한 자동 설명 생성 노드
    - 입력: state["code"]
    - 출력: state["auto_summary"], state["final_summary"](초기값은 auto_summary 복사)
    """
    code = state["code"]

    prompt = f"""
다음 소스코드가 무엇을 하는지 한국어로 3~5줄 정도로 요약해줘.
가능하면 함수/클래스 역할, 주된 비즈니스 로직을 구체적으로 써줘.

{code}
```
"""
    tool_log_id = start_tool_log(
            state,
            config,
            "Generating code summary"
        )

    try:
        auto_summary = get_llm_model("gemini").invoke(prompt)

        new_state: UnifiedState = {
            **state,
            "auto_summary": auto_summary,
            "final_summary": state.get("final_summary") or auto_summary, #  “사람이 수정한 값이 있으면 그걸 쓰고, 없으면 자동 요약을 쓰자”는 의미
        }
    finally:
        complete_tool_log(new_state, config)
        await asyncio.sleep(0)

    return new_state


def confirm_before_save_node(state: UnifiedState) -> Dict[str, Any]:
    """
    AG-UI용: 요약 확인 후 저장 여부 입력을 받기 위해 interrupt() 호출.
    재개 시 Command(resume={ "should_save": bool, "final_summary": str }) 가 반환됨.
    """
    payload = {
        "instruction": "요약을 확인하고, 수정이 있으면 final_summary에 넣어 주세요. 저장하려면 should_save를 true로 보내세요.",
        "auto_summary": state.get("auto_summary") or "",
        "final_summary": state.get("final_summary") or state.get("auto_summary") or "",
    }
    user_decision = interrupt(payload)
    if isinstance(user_decision, dict):
        should_save = user_decision.get("should_save", False)
        final_summary = user_decision.get("final_summary") or state.get("final_summary") or state.get("auto_summary") or ""
    else:
        should_save = False
        final_summary = state.get("final_summary") or state.get("auto_summary") or ""
    return {
        **state,
        "should_save": bool(should_save),
        "final_summary": final_summary,
    }


async def save_to_faiss_node(state: UnifiedState, config) -> Dict[str, Any]:
    """
    2단계: (사람이 설명을 확인/수정한 후) 최종 요약 + 코드 → 임베딩 → Faiss + Minio 저장
    should_save가 False면 아무 것도 하지 않고 통과
    """
    if not state.get("should_save"):
        # 저장하지 않고 그대로 반환
        return state
    user_id = state["user_id"]
    rag_minio = state["rag_minio"]
    code = state["code"]
    summary = state.get("final_summary") or state.get("auto_summary") or ""
    file_path = state.get("file_path") or "unknown"
    language = state.get("language") or "python"
    # ----- 1) 저장용 텍스트 구성 (설명 + 코드) -----
    # 검색 품질을 위해: 설명 + 파일경로 + 코드까지 전부 텍스트에 포함
    document_text = f"""
        [FILE] {file_path}
        [LANG] {language}
        [SUMMARY]
        {summary}
        [CODE]
        {code}
    """.strip()

    try:
        # ----- 2) 임베딩 계산 -----
        # OpenAIEmbeddings: embed_documents는 List[str] 입력
        embedding_vector = embeddings.embed_documents([document_text])[0]
        # ----- 3) 기존 Faiss index 로드 or 생성 -----
        # get_faiss_or_pickle(user_id, rag_minio) 는 예시용; 실제 구현에 맞게 조정
        index = get_faiss_or_pickle(user_id, rag_minio)
        # index는 faiss.IndexIDMap 가정
        # 간단히: user별 auto-increment id 대신, 여기선 hash 기반 id 예시
        # (실제 환경에서는 별도의 content_id를 state로 받아서 사용하는 게 더 좋음)
        content_id = faiss.IDSelectorBatch([hash(file_path + summary) & 0x7FFFFFFF])
        # faiss는 (N, d) 형태의 float32 배열이 필요



        vectors = np.array([embedding_vector], dtype="float32")
        ids = np.array([hash(file_path + summary) & 0x7FFFFFFF], dtype="int64")
        index.add_with_ids(vectors, ids)
        # ----- 4) Minio(S3)에 index 저장 -----
        # pickle.dumps 로 직렬화 후 user별 key에 저장
        serialized_index = pickle.dumps(index)
        # RAGSessionStore.put은 async 이므로 await
        await rag_minio.put(user_id, serialized_index)

    finally:
        complete_tool_log(state, config)
        await asyncio.sleep(0)


    return {
        **state,
        # 나중에 확인용 메타 정보 추가
        "saved_content_id": int(ids[0]),
    }