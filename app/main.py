"""FastAPI 入口文件。

负责创建应用实例，并挂载统一的 API 路由。
"""

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.api.routes import router
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.settings import settings
from app.db.session import init_db

configure_logging()
logger = get_logger(__name__)

# 创建整个后端服务的 FastAPI 应用对象。
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend for the Idea Validator MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize application resources on startup."""
    init_db()
    logger.info("Application startup complete.")


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """Attach a request id and log request latency."""
    request_id = str(uuid.uuid4())
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info("%s %s -> %s in %sms", request.method, request.url.path, response.status_code, duration_ms)
    return response


register_exception_handlers(app)

# 把定义好的接口路由注册到应用中。
app.include_router(router)
