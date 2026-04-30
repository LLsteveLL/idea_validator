"""历史检索节点。

从已保存的分析记录中召回相似 idea，作为后续总结时的参考上下文。
"""

from app.core.logging import get_logger
from app.services.retrieval import retrieve_similar_analyses
from app.schemas.state import GraphState

logger = get_logger(__name__)


def retrieve_history(state: GraphState) -> dict:
    """Retrieve similar historical analyses from the local SQLite store."""
    clarified = state["clarified_input"]

    try:
        similar_analyses = retrieve_similar_analyses(clarified)
        logger.info("Retrieved %s similar analyses", len(similar_analyses))
        return {"similar_analyses": similar_analyses}
    except Exception as exc:
        logger.warning("History retrieval failed: %s", exc)
        return {"similar_analyses": []}
