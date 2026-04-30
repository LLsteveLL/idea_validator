"""输入模型。

这个文件定义用户提交给系统的请求体结构。
`IdeaInput` 代表用户从前端表单传入的创业想法信息，
是整个分析流程的起点，用来约束用户必须提供哪些字段。
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class IdeaInput(BaseModel):
    """用户提交的创业 idea 输入数据。

    这个模型用于：
    - 校验前端传来的请求格式是否正确
    - 统一后端分析流程的输入结构
    - 作为 LangGraph 初始状态里的原始输入
    """
    idea: str
    """创业想法本身，用户想做的产品或服务是什么。"""

    target_user: str
    """目标用户是谁，描述最核心的受众群体。"""

    problem: str
    """用户要解决的核心痛点或问题。"""

    monetization: Optional[str] = None
    """计划如何赚钱，例如订阅、一次性付费、佣金等。"""

    resources: Optional[str] = None
    """当前已有资源，例如技术能力、行业资源、团队背景等。"""

    stage: Optional[str] = None
    """当前所处阶段，例如只有想法、已有原型、已有用户。"""

    geography: Optional[str] = None
    """目标市场的地域范围，例如中国、美国、全球。"""

    notes: Optional[str] = None
    """额外补充信息，用来承载表单中放不下的上下文。"""
