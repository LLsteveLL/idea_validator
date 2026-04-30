"""验证计划节点。

把抽象分析结果转换成可以执行的低成本验证动作。
"""

from pydantic import BaseModel, Field

from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.schemas.state import GraphState


class ValidationPlan(BaseModel):
    """验证计划的结构化输出。"""

    key_assumptions_to_test: list[str] = Field(description="The assumptions that should be tested first.")
    experiments: list[str] = Field(description="Concrete validation experiments.")
    success_metrics: list[str] = Field(description="Signals that would count as positive validation.")
    recommended_next_step: str = Field(description="The single best immediate next step.")


def _fallback_validation_plan(clarified: dict) -> dict:
    """LLM 失败时使用的基础验证计划。"""
    return {
        "key_assumptions_to_test": [
            f"{clarified['target_user']} care enough about this problem to try a new solution",
            "They will understand the value proposition quickly",
            "At least some users are willing to pay",
        ],
        "experiments": [
            "Interview 5 target users",
            "Create a landing page with one clear promise",
            "Collect waitlist signups or demo requests",
        ],
        "success_metrics": [
            "At least 3 of 5 interviews confirm the problem is painful",
            "Landing page converts above a baseline threshold",
            "Some users express willingness to pay or book a demo",
        ],
        "recommended_next_step": "Run a narrow landing-page test before building the product.",
    }


def validation_planner(state: GraphState) -> dict:
    """生成关键假设、实验方案和成功指标。"""
    clarified = state["clarified_input"]

    prompt = render_prompt("validation", risk=state.get("risk", {}), **clarified)

    try:
        llm = get_chat_model(temperature=0.2)
        structured_llm = llm.with_structured_output(ValidationPlan)
        validation = structured_llm.invoke(prompt)
        return {"validation": validation.model_dump()}
    except Exception:
        return {"validation": _fallback_validation_plan(clarified)}
