"""LLM 服务辅助函数。"""

from langchain_openai import ChatOpenAI

from app.core.settings import settings


def get_openai_api_key() -> str:
    """读取 OpenAI API Key；如果缺失则抛出明确错误。"""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please add it to your .env file.")
    return settings.openai_api_key


def get_chat_model(model: str | None = None, temperature: float = 0.2) -> ChatOpenAI:
    """创建一个可供 graph 节点复用的 ChatOpenAI 实例。"""
    return ChatOpenAI(
        model=model or settings.openai_model,
        temperature=temperature,
        api_key=get_openai_api_key(),
        timeout=settings.request_timeout_seconds,
    )
