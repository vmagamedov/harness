"""
    aiohttp
    =======

    Wires for the aiohttp_ project.

    .. _aiohttp: https://github.com/aio-libs/aiohttp
"""
from http import HTTPStatus
from typing import TYPE_CHECKING, Callable, Awaitable, List, Dict, Optional
from logging import Logger

from aiohttp.web_runner import AppRunner, TCPSite
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_exceptions import HTTPException
from aiohttp.web_middlewares import middleware

from opentelemetry.trace import SpanKind, tracer
from opentelemetry.propagators import extract
from opentelemetry.trace.status import Status, StatusCanonicalCode

from .. import http_pb2
from .base import Wire, WaitMixin

if TYPE_CHECKING:
    from aiohttp.web import Application


def _headers_getter(request: Request, header_name: str) -> List[str]:
    return request.headers.getall(header_name, [])


_HTTP_STATUS_TO_CODE_MAP: Dict[int, StatusCanonicalCode] = {
    # 401
    HTTPStatus.UNAUTHORIZED.value: StatusCanonicalCode.UNAUTHENTICATED,
    # 403
    HTTPStatus.FORBIDDEN.value: StatusCanonicalCode.PERMISSION_DENIED,
    # 404
    HTTPStatus.NOT_FOUND.value: StatusCanonicalCode.NOT_FOUND,
    # 429
    HTTPStatus.TOO_MANY_REQUESTS.value: StatusCanonicalCode.RESOURCE_EXHAUSTED,
    # 501
    HTTPStatus.NOT_IMPLEMENTED.value: StatusCanonicalCode.UNIMPLEMENTED,
    # 503
    HTTPStatus.SERVICE_UNAVAILABLE.value: StatusCanonicalCode.UNAVAILABLE,
    # 504
    HTTPStatus.GATEWAY_TIMEOUT.value: StatusCanonicalCode.DEADLINE_EXCEEDED,
}


def _status_to_canonical_code(status_code: int):
    try:
        return _HTTP_STATUS_TO_CODE_MAP[status_code]
    except KeyError:
        if status_code < 100:
            return StatusCanonicalCode.UNKNOWN
        elif status_code < 400:
            return StatusCanonicalCode.OK
        elif status_code < 500:
            return StatusCanonicalCode.INVALID_ARGUMENT
        elif status_code < 600:
            return StatusCanonicalCode.INTERNAL
        else:
            return StatusCanonicalCode.UNKNOWN


@middleware
async def _opentracing_middleware(
    request: Request,
    handler: Callable[[Request], Awaitable[Response]],
) -> Response:
    tracer_ = tracer()
    parent_span = extract(_headers_getter, request)
    with tracer_.start_as_current_span(
        request.path,
        parent_span,
        kind=SpanKind.SERVER,
        attributes={
            "component": "http",
            "http.method": request.method,
            "http.scheme": request.scheme,
            "http.host": request.host,
        },
    ) as span:
        try:
            response = await handler(request)
        except HTTPException as e:
            code = _status_to_canonical_code(e.status)
            span.set_status(Status(code))
            span.set_attribute("http.status_text", e.reason)
            raise
        else:
            code = _status_to_canonical_code(response.status)
            span.set_status(Status(code))
            span.set_attribute("http.status_text", response.reason)
            return response


class ServerWire(WaitMixin, Wire):
    """
    Output wire to start HTTP server and serve aiohttp application.
    """
    _runner = None
    _site = None
    _site_factory = None

    def __init__(
        self, app: 'Application', *, access_log: Optional[Logger] = None,
    ) -> None:
        """
        :Configurable by: :proto:message:`harness.http.Server`

        :param app: configured :py:class:`aiohttp:aiohttp.web.Application`
            to run
        :param access_log: enable access logs by providing a logger instance
        """
        self._app = app
        self._access_log = access_log

    def configure(self, value: http_pb2.Server):
        assert isinstance(value, http_pb2.Server), type(value)

        self._app.middlewares.append(_opentracing_middleware)
        self._runner = AppRunner(self._app, access_log=self._access_log)
        self._site_factory = lambda: TCPSite(
            self._runner,
            value.bind.host or '127.0.0.1',
            value.bind.port or 8000,
        )

    async def __aenter__(self):
        await self._runner.setup()
        self._site = self._site_factory()
        await self._site.start()
        print(f'Started Web server and listening on {self._site.name}')

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._runner.cleanup()
