"""
AEGIS INVEST — Request ID Middleware
Ensures every incoming HTTP request is assigned a unique UUIDv4 identifier
which propagates across logging contexts and appears in response headers.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_ctx

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Extracts or generates an X-Request-ID for every HTTP request.
    Binds the ID to the contextvar for contextual logging and appends to response headers.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming_req_id = request.headers.get(REQUEST_ID_HEADER)
        req_id = incoming_req_id.strip() if incoming_req_id else str(uuid.uuid4())

        # Set contextvar for the duration of this async task
        token = request_id_ctx.set(req_id)
        # Also attach to request.state for convenient route-handler access
        request.state.request_id = req_id

        try:
            response: Response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = req_id
            return response
        finally:
            request_id_ctx.reset(token)
