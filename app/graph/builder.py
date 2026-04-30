"""LangGraph 构建与执行入口。

这里负责：
- 注册各个分析节点
- 定义节点执行顺序
- 提供统一的 graph 调用函数
"""

from langgraph.graph import END, START, StateGraph

from app.graph.nodes.business_agent import business_agent
from app.graph.nodes.clarify_idea import clarify_idea
from app.graph.nodes.competitor_agent import competitor_agent
from app.graph.nodes.final_synthesizer import final_synthesizer
from app.graph.nodes.market_agent import market_agent
from app.graph.nodes.plan_analysis import plan_analysis
from app.graph.nodes.retrieve_history import retrieve_history
from app.graph.nodes.risk_agent import risk_agent
from app.graph.nodes.validation_planner import validation_planner
from app.schemas.input import IdeaInput
from app.schemas.output import FinalReport
from app.schemas.state import GraphState


def build_graph():
    """构建第一版串行执行的 LangGraph 工作流。"""
    # `GraphState` 定义了整个 graph 在节点间共享的数据结构。
    graph = StateGraph(GraphState)

    # 注册节点：每个节点负责一个独立分析步骤。
    graph.add_node("clarify_idea", clarify_idea)
    graph.add_node("retrieve_history", retrieve_history)
    graph.add_node("plan_analysis", plan_analysis)
    graph.add_node("market_agent", market_agent)
    graph.add_node("competitor_agent", competitor_agent)
    graph.add_node("business_agent", business_agent)
    graph.add_node("risk_agent", risk_agent)
    graph.add_node("validation_planner", validation_planner)
    graph.add_node("final_synthesizer", final_synthesizer)

    # 定义串行执行路径，让状态从输入一路流到最终汇总。
    graph.add_edge(START, "clarify_idea")
    graph.add_edge("clarify_idea", "retrieve_history")
    graph.add_edge("retrieve_history", "plan_analysis")
    graph.add_edge("plan_analysis", "market_agent")
    graph.add_edge("market_agent", "competitor_agent")
    graph.add_edge("competitor_agent", "business_agent")
    graph.add_edge("business_agent", "risk_agent")
    graph.add_edge("risk_agent", "validation_planner")
    graph.add_edge("validation_planner", "final_synthesizer")
    graph.add_edge("final_synthesizer", END)

    # 编译后返回可直接 invoke 的 graph 对象。
    return graph.compile()


def run_analysis(idea_input: IdeaInput) -> GraphState:
    """运行 graph，并返回包含全部中间结果的内部状态。"""
    compiled_graph = build_graph()
    # 初始状态只需要放入用户输入，其他字段由后续节点逐步补齐。
    initial_state: GraphState = {
        "input": idea_input.model_dump(),
        "errors": [],
    }
    return compiled_graph.invoke(initial_state)


def analyze_idea(idea_input: IdeaInput) -> FinalReport:
    """运行 graph，并只返回最终对外暴露的报告结果。"""
    result = run_analysis(idea_input)
    return FinalReport(**result["final"])


def analyze_idea_with_state(idea_input: IdeaInput) -> tuple[FinalReport, GraphState]:
    """运行 graph，并同时返回最终报告和完整状态。"""
    result = run_analysis(idea_input)
    return FinalReport(**result["final"]), result
