"""API 路由定义。

这里负责暴露对外可访问的 HTTP 接口。
"""

from fastapi import APIRouter

from app.core.errors import AppError
from app.core.logging import get_logger
from app.core.settings import settings
from app.db.session import load_analysis_by_id, load_recent_analyses, save_analysis
from app.graph.builder import analyze_idea_with_state
from app.schemas.input import IdeaInput
from app.schemas.output import AnalysisDetail, AnalysisListItem, FinalReport

# 统一管理本模块下的接口路由。
router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
def health_check() -> dict:
    """健康检查接口。

    用于确认服务是否成功启动并可正常响应请求。
    """
    return {"status": "ok"}


@router.get("/analyses", response_model=list[AnalysisListItem])
def list_analyses(limit: int = 20) -> list[AnalysisListItem]:
    """返回最近保存的分析摘要列表。"""
    rows = load_recent_analyses(limit=limit)
    return [
        AnalysisListItem(
            id=row["id"],
            created_at=row["created_at"],
            idea=row["idea_input"].get("idea", ""),
            target_user=row["idea_input"].get("target_user", ""),
            verdict=row["final_report"].get("verdict"),
            overall_score=row["final_report"].get("overall_score"),
            summary=row["final_report"].get("summary", ""),
        )
        for row in rows
    ]


@router.get("/analyses/{analysis_id}", response_model=AnalysisDetail)
def get_analysis(analysis_id: int) -> AnalysisDetail:
    """返回单条历史分析详情。"""
    row = load_analysis_by_id(analysis_id)
    if row is None:
        raise AppError("Analysis not found.", status_code=404)

    return AnalysisDetail(
        id=row["id"],
        created_at=row["created_at"],
        idea_input=row["idea_input"],
        final_report=row["final_report"],
    )


@router.post("/analyze", response_model=FinalReport)
def analyze(payload: IdeaInput) -> FinalReport:
    """运行 idea 分析主流程并返回最终报告。"""
    try:
        report, graph_state = analyze_idea_with_state(payload)
        if settings.save_analysis_results:
            analysis_id = save_analysis(
                idea_input=payload.model_dump(),
                graph_state=graph_state,
                final_report=report.model_dump(),
            )
            report.analysis_id = analysis_id
        return report
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Failed to analyze idea: %s", exc)
        raise AppError("Failed to analyze idea.", status_code=500) from exc
