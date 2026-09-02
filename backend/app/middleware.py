from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from threading import Lock
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import Settings

logger = logging.getLogger("manakai")


class StagingSafetyMiddleware(BaseHTTPMiddleware):
    """Anonymous staging safeguards; use a shared limiter before horizontal scaling."""

    def __init__(self, app, config: Settings):
        super().__init__(app)
        self.config = config
        self.requests: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def _client_ip(self, request: Request) -> str:
        if self.config.trust_proxy_headers:
            forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            if forwarded:
                return forwarded
        return request.client.host if request.client else "unknown"

    def _limit_for(self, request: Request) -> tuple[str, int] | None:
        if request.method != "POST":
            return None
        path = request.url.path
        if path == "/api/v1/chat" or (path.startswith("/api/v1/conversations/") and path.endswith("/messages")):
            return "chat", self.config.chat_rate_limit_requests
        if path in {"/api/v1/products/analyse", "/api/v1/compliance/analyse"}:
            return "analysis", self.config.analysis_rate_limit_requests
        return None

    def _allowed(self, key: tuple[str, str], limit: int, now: float) -> tuple[bool, int]:
        cutoff = now - self.config.rate_limit_window_seconds
        with self.lock:
            bucket = self.requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False, max(1, int(bucket[0] + self.config.rate_limit_window_seconds - now))
            bucket.append(now)
        return True, 0

    async def dispatch(self, request: Request, call_next):
        started = time.perf_counter()
        request_id = request.headers.get("x-request-id", "")[:64] or uuid4().hex
        request.state.request_id = request_id
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > self.config.max_request_body_bytes:
            return JSONResponse({"detail": "Request body is too large"}, status_code=413, headers={"X-Request-ID": request_id})
        if request.method in {"POST", "PUT", "PATCH"}:
            body = await request.body()
            if len(body) > self.config.max_request_body_bytes:
                return JSONResponse({"detail": "Request body is too large"}, status_code=413, headers={"X-Request-ID": request_id})
        rule = self._limit_for(request)
        if rule:
            bucket_name, limit = rule
            allowed, retry_after = self._allowed((self._client_ip(request), bucket_name), limit, time.time())
            if not allowed:
                logger.warning("rate_limit_exceeded request_id=%s route=%s bucket=%s", request_id, request.url.path, bucket_name)
                return JSONResponse(
                    {"detail": "Rate limit exceeded. Please try again shortly."}, status_code=429,
                    headers={"Retry-After": str(retry_after), "X-Request-ID": request_id},
                )
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed request_id=%s route=%s", request_id, request.url.path)
            raise
        latency_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.scheme == "https" or self.config.app_env == "staging":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        logger.info(
            "request_complete request_id=%s route=%s status_code=%s latency_ms=%.2f",
            request_id, request.url.path, response.status_code, latency_ms,
        )
        return response
