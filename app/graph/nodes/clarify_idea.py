"""输入澄清节点。

把用户原始输入整理成更稳定的中间结构，供后续节点统一使用。
"""

from pydantic import BaseModel, Field

from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.schemas.state import GraphState


class ClarifiedIdea(BaseModel):
    """澄清后的 idea 结构化结果。

    这个 schema 约束 LLM 必须返回稳定字段，避免后续节点读取漂移。
    """

    idea: str = Field(description="A concise restatement of the product or startup idea.")
    target_user: str = Field(description="The clearest definition of the target audience.")
    problem: str = Field(description="The core user problem this idea is trying to solve.")
    monetization: str = Field(description="The monetization approach, or 'Not provided' if unclear.")
    resources: str = Field(description="Available founder or team resources, or 'Not provided'.")
    stage: str = Field(description="Current project stage, such as idea, prototype, or early users.")
    geography: str = Field(description="Target market geography, or 'Global' if not specified.")
    notes: str = Field(description="Additional relevant notes that help downstream analysis.")


def _fallback_clarified_idea(idea_input: dict) -> dict:
    """当 LLM 不可用或返回失败时，回退到本地标准化逻辑。"""
    return {
        "idea": idea_input["idea"].strip(),
        "target_user": idea_input["target_user"].strip(),
        "problem": idea_input["problem"].strip(),
        "monetization": (idea_input.get("monetization") or "Not provided").strip(),
        "resources": (idea_input.get("resources") or "Not provided").strip(),
        "stage": (idea_input.get("stage") or "idea").strip(),
        "geography": (idea_input.get("geography") or "Global").strip(),
        "notes": (idea_input.get("notes") or "").strip(),
    }


def clarify_idea(state: GraphState) -> dict:
    """使用 LLM 澄清输入；若失败则回退到本地标准化逻辑。"""
    idea_input = state["input"]

    # Prompt 外置到文件，便于单独迭代分析策略而不混入节点逻辑。
    prompt = render_prompt(
        "clarify",
        idea=idea_input.get("idea", ""),
        target_user=idea_input.get("target_user", ""),
        problem=idea_input.get("problem", ""),
        monetization=idea_input.get("monetization") or "",
        resources=idea_input.get("resources") or "",
        stage=idea_input.get("stage") or "",
        geography=idea_input.get("geography") or "",
        notes=idea_input.get("notes") or "",
    )

    try:
        llm = get_chat_model(temperature=0)
        structured_llm = llm.with_structured_output(ClarifiedIdea)
        clarified = structured_llm.invoke(prompt)
        return {"clarified_input": clarified.model_dump()}
    except Exception:
        # 第一版不要因为 LLM 或密钥配置问题直接让整条 graph 失败。
        clarified = _fallback_clarified_idea(idea_input)
        return {"clarified_input": clarified}
