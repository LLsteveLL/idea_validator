"""分析计划节点。

根据澄清后的 idea，生成一份简化的分析步骤说明。
"""

from app.schemas.state import GraphState


def plan_analysis(state: GraphState) -> dict:
    """生成后续节点要执行的分析计划。"""
    clarified = state["clarified_input"]

    # 第一版先用固定模板计划，后续可以按 idea 类型动态生成。
    plan = [
        f"Assess demand for {clarified['target_user']}",
        "Review direct competitors and substitutes",
        "Check business model clarity and monetization path",
        "Highlight main execution and market risks",
        "Recommend a low-cost validation plan",
    ]
    return {"plan": plan}
