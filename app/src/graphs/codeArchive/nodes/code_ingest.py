from typing import Dict, Any
import asyncio
import pickle
import numpy as np
import time

from langgraph.types import interrupt

from app.src.graphs.codeArchive.state import UnifiedState
from app.src.services.llm import get_llm_model
from app.src.services.embeddings import get_embedding
from app.src.utils.tool_logs import complete_tool_log, start_tool_log


async def generate_code_summary_node(state: UnifiedState, config) -> Dict[str, Any]:
    """
    1단계: 코드에 대한 자동 설명 생성 노드
    - 입력: state["code"]
    - 출력: state["auto_summary"]
    """
    code = state["code"]

    prompt = f"""
다음 소스코드가 무엇을 하는지 한국어로 4~5줄 정도로 요약해줘.
가능하면 함수/클래스 역할, 주된 비즈니스 로직을 구체적으로 써줘.

{code}
```
"""
    # tool_log_id = start_tool_log(
    #         state,
    #         config,
    #         "Generating code summary"
    #     )

    try:
        auto_summary = get_llm_model("gemini").invoke(prompt)

        new_state: UnifiedState = {
            **state,
            "auto_summary": auto_summary
            # "final_summary": state.get("final_summary") or auto_summary, #  “사람이 수정한 값이 있으면 그걸 쓰고, 없으면 자동 요약을 쓰자”는 의미
        }
    finally:
        # complete_tool_log(new_state, config)
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
    rag_minio = config["configurable"]["minio_client"]
    content_minio = config["configurable"]["rag_content_minio"]
    code = state["code"]
    summary = state.get("auto_summary")
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


    def generate_id(counter=[0]):
        ts = int(time.time() * 1000)  # milliseconds
        counter[0] = (counter[0] + 1) % 1000
        return np.int64(ts * 1000 + counter[0])

    try:
        
        encode_content = get_embedding("gemini").embed_query(summary.content) #요약문만 임베딩
        embed_content = np.array(encode_content).reshape(1, -1).astype("float32")

        index = rag_minio.get(user_id=user_id, dim=embed_content.shape[1])
        user_content = content_minio.get(user_id=user_id)

        generate_key = generate_id()
        ids = np.array([generate_key], dtype=np.int64)

        user_content[str(generate_key)] = document_text #저장은 전체 내용으로

    
        index.add_with_ids(embed_content, ids)

        rag_minio.put(user_id, pickle.dumps(index))
        content_minio.put(user_id, pickle.dumps(user_content))

    except Exception as e:
        return {
            **state,
            "error": str(e),
            "error_node": "save_to_faiss_node"
        }

    finally:
        # complete_tool_log(state, config)
        await asyncio.sleep(0)

    print(state)


    return {
        **state,
        # 나중에 확인용 메타 정보 추가
        "saved_content_id": generate_key,
    }