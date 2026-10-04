import logging
import uuid
from collections.abc import Iterable
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from services.api.configuration import APIConfiguration
from services.api.models import (
    ErrorResponse,
    HealthResponse,
    ProcessRequest,
    ResumeRequest,
)
from services.api.sse import encode_sse
from services.errors.exceptions import AIError, InvalidRequestError
from services.errors.translate import normalize_exception
from services.observability.langsmith import get_langsmith_status
from services.streaming.emitter import StreamEmitter


logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _error_response(
    request: Request,
    error: AIError,
    *,
    debug: bool,
) -> JSONResponse:
    show_details = debug or error.status_code < 500
    details: Any = error.details if show_details else None

    payload = ErrorResponse(
        code=error.code,
        message=error.message,
        details=details,
        request_id=_get_request_id(request),
    )

    return JSONResponse(
        status_code=error.status_code,
        content=payload.model_dump(mode="json"),
        headers={
            "X-Request-ID": _get_request_id(request),
        },
    )


def create_app(
    brain,
    configuration: APIConfiguration | None = None,
) -> FastAPI:
    configuration = configuration or APIConfiguration.from_env()

    app = FastAPI(
        title=configuration.service_name,
        version=configuration.version,
        debug=configuration.debug,
    )

    if configuration.cors_origins:
        allow_credentials = "*" not in configuration.cors_origins
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(configuration.cors_origins),
            allow_credentials=allow_credentials,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

    app.state.brain = brain
    app.state.configuration = configuration

    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(AIError)
    async def ai_error_handler(request: Request, exc: AIError):
        return _error_response(
            request,
            exc,
            debug=configuration.debug,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        error = InvalidRequestError(
            "Request validation failed.",
            details=jsonable_encoder(exc.errors()),
        )
        error.status_code = 422
        return _error_response(
            request,
            error,
            debug=configuration.debug,
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        error = normalize_exception(exc)
        logger.exception(
            "Unhandled AI API error request_id=%s",
            _get_request_id(request),
        )
        return _error_response(
            request,
            error,
            debug=configuration.debug,
        )

    def event_stream(events: Iterable, request: Request):
        emitter = StreamEmitter()

        try:
            for event in events:
                yield encode_sse(event)
        except Exception as exc:
            error = normalize_exception(exc)
            logger.exception(
                "Unhandled streaming error request_id=%s",
                _get_request_id(request),
            )
            yield encode_sse(
                emitter.error(
                    error.message,
                    code=error.code,
                    details={
                        "request_id": _get_request_id(request),
                    },
                )
            )

    @app.get("/health", response_model=HealthResponse)
    def health():
        langsmith_status = get_langsmith_status()
        return HealthResponse(
            status="ok",
            service=configuration.service_name,
            version=configuration.version,
            langsmith_enabled=langsmith_status["enabled"],
        )

    @app.post(f"{configuration.prefix}/process")
    def process(payload: ProcessRequest, request: Request):
        if len(payload.question) > configuration.max_question_chars:
            raise InvalidRequestError(
                "Question exceeds the configured maximum length.",
                details={
                    "max_question_chars": configuration.max_question_chars,
                },
            )

        if len(payload.session_id) > configuration.max_session_id_chars:
            raise InvalidRequestError(
                "Session ID exceeds the configured maximum length.",
                details={
                    "max_session_id_chars": configuration.max_session_id_chars,
                },
            )

        return request.app.state.brain.process(
            question=payload.question,
            session_id=payload.session_id,
        )

    @app.post(f"{configuration.prefix}/resume")
    def resume(payload: ResumeRequest, request: Request):
        if len(payload.session_id) > configuration.max_session_id_chars:
            raise InvalidRequestError(
                "Session ID exceeds the configured maximum length.",
                details={
                    "max_session_id_chars": configuration.max_session_id_chars,
                },
            )

        return request.app.state.brain.resume(
            session_id=payload.session_id,
            approved=payload.approved,
        )

    @app.post(f"{configuration.prefix}/stream")
    def stream(payload: ProcessRequest, request: Request):
        if len(payload.question) > configuration.max_question_chars:
            raise InvalidRequestError(
                "Question exceeds the configured maximum length.",
            )
        if len(payload.session_id) > configuration.max_session_id_chars:
            raise InvalidRequestError(
                "Session ID exceeds the configured maximum length.",
            )

        events = request.app.state.brain.stream(
            question=payload.question,
            session_id=payload.session_id,
        )

        return StreamingResponse(
            event_stream(events, request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    @app.post(f"{configuration.prefix}/resume/stream")
    def resume_stream(payload: ResumeRequest, request: Request):
        if len(payload.session_id) > configuration.max_session_id_chars:
            raise InvalidRequestError(
                "Session ID exceeds the configured maximum length.",
            )

        events = request.app.state.brain.resume_stream(
            session_id=payload.session_id,
            approved=payload.approved,
        )

        return StreamingResponse(
            event_stream(events, request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    return app
