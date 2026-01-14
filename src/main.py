from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

import structlog

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .dependencies import close_resources, get_logger, init_resources
from .metrics import metrics_app
from .api import chat, metrics, system, topology


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context:
    - Initialize shared resources (DB engine, Redis, LangGraph graph, etc.)
    - Clean them up on shutdown
    """
    await init_resources()
    try:
        yield
    finally:
        await close_resources()


def create_app() -> FastAPI:
    """
    Application factory for the topology agent API.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        docs_url=f"{settings.api_prefix.rstrip('/')}/docs",
        openapi_url=f"{settings.api_prefix.rstrip('/')}/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------ #
    # Request ID middleware (correlation IDs)
    # ------------------------------------------------------------------ #
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        # Reuse header if present, otherwise generate one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        # Attach it to the request state so handlers can access it
        request.state.request_id = request_id

        # Bind to structlog's context for this coroutine
        logger = structlog.get_logger("http").bind(request_id=request_id)
        logger.info(
            "http_request_start",
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
        finally:
            logger.info("http_request_end", path=request.url.path)

        # Echo it back in the response headers
        response.headers["X-Request-ID"] = request_id
        return response

    # Router registration
    api_prefix = settings.api_prefix.rstrip("/")

    app.include_router(system.router, prefix=api_prefix)
    app.include_router(chat.router, prefix=api_prefix)
    app.include_router(topology.router, prefix=api_prefix)

    # Mount the separate metrics app for multi-process mode
    app.mount("/metrics", metrics_app)

    return app


# ASGI entrypoint for uvicorn / hypercorn, etc.
# e.g. uvicorn src.main:app --reload
app = create_app()
