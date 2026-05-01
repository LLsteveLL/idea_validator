"""输出模型。

这个文件定义系统最终返回给前端的结构化结果。
`FinalReport` 代表一次 idea 分析完成后的最终结论，
用于约束 API 响应格式，保证前端可以稳定渲染结果页面。
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ScoreExplanation(BaseModel):
    """单个评分维度的解释。"""

    score: int = Field(ge=0, le=100)
    """该维度的原始分数。"""

    weighted_score: int = Field(ge=0, le=100)
    """该维度加权后的贡献分。"""

    rationale: str
    """这一维度为什么得到这个分数。"""

    positive_signals: List[str]
    """拉高该维度分数的证据或信号。"""

    negative_signals: List[str]
    """拉低该维度分数的证据或信号。"""


class LocalizedScoreExplanationText(BaseModel):
    """某个评分维度的本地化文本解释。"""

    rationale: str
    positive_signals: List[str]
    negative_signals: List[str]


class LocalizedScoreExplanationTextSet(BaseModel):
    """四个维度的本地化评分解释文本。"""

    market: LocalizedScoreExplanationText
    competition: LocalizedScoreExplanationText
    business: LocalizedScoreExplanationText
    risk: LocalizedScoreExplanationText


class ScoreExplanationSet(BaseModel):
    """四个核心维度的评分解释。"""

    market: ScoreExplanation
    competition: ScoreExplanation
    business: ScoreExplanation
    risk: ScoreExplanation


class LocalizedNarrative(BaseModel):
    """某种语言下的报告文本内容。"""

    summary: str
    opportunities: List[str]
    risks: List[str]
    key_assumptions: List[str]
    next_steps: List[str]
    score_explanations: LocalizedScoreExplanationTextSet


class ReportTranslations(BaseModel):
    """中英文双语报告内容。"""

    en: LocalizedNarrative
    zh: LocalizedNarrative


class EvidenceItem(BaseModel):
    """展示给前端的证据条目。"""

    title: str
    """证据标题。"""

    url: Optional[str] = None
    """证据链接。"""

    summary: str
    """证据摘要。"""


class SimilarAnalysisEvidence(BaseModel):
    """相似历史分析摘要。"""

    analysis_id: Optional[int] = None
    similarity: float
    idea: str
    verdict: Optional[str] = None
    overall_score: Optional[int] = None
    summary: str


class ReportEvidence(BaseModel):
    """最终报告中的可见证据集合。"""

    market_search: List[EvidenceItem]
    competitor_search: List[EvidenceItem]
    similar_analyses: List[SimilarAnalysisEvidence]


class ScoreBreakdown(BaseModel):
    """分项评分结果。"""

    market: int = Field(ge=0, le=100)
    """市场维度原始分数。"""

    competition: int = Field(ge=0, le=100)
    """竞争维度原始分数。"""

    business: int = Field(ge=0, le=100)
    """商业模式维度原始分数。"""

    risk: int = Field(ge=0, le=100)
    """风险调整后的分数，越高表示越安全。"""

    weighted_market: int = Field(ge=0, le=100)
    """市场维度加权后贡献分。"""

    weighted_competition: int = Field(ge=0, le=100)
    """竞争维度加权后贡献分。"""

    weighted_business: int = Field(ge=0, le=100)
    """商业模式维度加权后贡献分。"""

    weighted_risk: int = Field(ge=0, le=100)
    """风险维度加权后贡献分。"""

    overall_score: int = Field(ge=0, le=100)
    """最终总分。"""


class FinalReport(BaseModel):
    """最终分析报告。

    这个模型用于：
    - 统一 `/analyze` 接口的返回格式
    - 约束最终 verdict、分数和建议字段
    - 防止不同节点输出漂移后影响前端展示
    """

    verdict: Literal["go", "narrow", "no-go"]
    """最终判断结果：值得做、建议缩小切口、或暂时不建议做。"""

    overall_score: int = Field(ge=0, le=100)
    """整体可行性评分，范围 0 到 100。"""

    score_breakdown: ScoreBreakdown
    """分项评分明细，便于解释总分由哪些维度组成。"""

    score_explanations: ScoreExplanationSet
    """每个评分维度的解释，以及拉高/拉低分数的证据。"""

    translations: ReportTranslations
    """结果页可切换显示的中英文版本。"""

    summary: str
    """对整个 idea 的简要总结，说明为什么得到这个结论。"""

    opportunities: List[str]
    """这个 idea 当前看到的主要机会点。"""

    risks: List[str]
    """这个 idea 最重要的风险点。"""

    key_assumptions: List[str]
    """决定成败的关键假设，后续需要优先验证。"""

    next_steps: List[str]
    """建议用户接下来执行的具体动作。"""

    evidence: ReportEvidence
    """用于支撑判断的 search/retrieval 证据摘要。"""

    analysis_id: Optional[int] = None
    """持久化后的分析记录 ID，便于后续查询历史结果。"""


class AnalysisListItem(BaseModel):
    """历史分析列表项。"""

    id: int
    """分析记录 ID。"""

    created_at: str
    """记录创建时间。"""

    idea: str
    """原始 idea 文本。"""

    target_user: str
    """目标用户。"""

    verdict: Optional[str] = None
    """历史分析的结论。"""

    overall_score: Optional[int] = None
    """历史分析的总分。"""

    summary: str = ""
    """历史分析摘要。"""


class AnalysisDetail(BaseModel):
    """单条历史分析详情。"""

    id: int
    """分析记录 ID。"""

    created_at: str
    """记录创建时间。"""

    idea_input: dict
    """原始输入。"""

    final_report: dict
    """最终报告。"""
