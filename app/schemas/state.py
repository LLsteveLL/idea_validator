"""LangGraph 状态模型。

这个文件定义分析流程在内部流转时使用的状态结构。
`GraphState` 不直接暴露给前端，而是给 LangGraph 各个节点共享、
读取和更新的中间数据容器。
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, TypedDict

class GraphState(TypedDict, total=False):
    """LangGraph 内部状态。

    这个模型用于：
    - 规定各个节点之间通过什么字段传递数据
    - 保存中间分析结果，例如 market、risk、validation
    - 让整个 graph 的执行链路更稳定、更容易维护
    """
    input: dict
    """用户提交的原始输入，是 graph 的起始数据。"""

    clarified_input: dict
    """经过澄清和标准化后的输入，供后续节点统一使用。"""

    plan: list[str]
    """分析计划，说明后续节点准备从哪些维度展开评估。"""

    market: dict
    """市场分析结果，例如需求强度、用户痛点、市场信号。"""

    competitors: dict
    """竞品与替代方案分析结果。"""

    market_search_results: list[dict]
    """市场分析阶段检索到的外部搜索结果。"""

    competitor_search_results: list[dict]
    """竞品分析阶段检索到的外部搜索结果。"""

    similar_analyses: list[dict]
    """从本地历史分析记录中召回的相似 idea。"""

    business: dict
    """商业模式分析结果，例如变现清晰度、获客难度、交付复杂度。"""

    risk: dict
    """风险分析结果，包括主要风险、隐藏假设和整体风险水平。"""

    validation: dict
    """验证计划结果，包含实验建议、成功指标和下一步动作。"""

    final: dict
    """最终汇总后的报告数据，通常会映射到 FinalReport。"""

    errors: list[str]
    """执行过程中记录的错误信息，便于调试和回溯。"""
