"""Prompt loading helpers.

负责从 `app/prompts/` 目录读取模板，并用上下文变量格式化。
"""

from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt_template(name: str) -> str:
    """读取指定 prompt 模板原文。"""
    prompt_path = PROMPTS_DIR / f"{name}.txt"
    return prompt_path.read_text(encoding="utf-8").strip()


def render_prompt(name: str, **context: object) -> str:
    """读取并格式化 prompt 模板。"""
    template = load_prompt_template(name)
    return template.format(**context)
