from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[1] / "graphs"


def load_prompt(graph_name:str, filename: str) -> str:
    path = PROMPT_DIR / graph_name / "prompt" / filename 
    return path.read_text(encoding="utf-8")
