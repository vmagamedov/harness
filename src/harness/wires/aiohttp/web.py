import logging
import ipaddress
from http import HTTPStatus
from typing import Callable, Awaitable, List, Dict, Optional
from logging import Logger

from aiohttp.web import Application, AppRunner, TCPSite, Request, Response
from aiohttp.web import HTTPException, middleware

from opentelemetry.trace import get_tracer, SpanKind
from opentelemetry.context import attach
from opentelemetry.propagators import extract
from opentelemetry.trace.status import Status, StatusCanonicalCode

from ... import http_pb2

from ..base import Wire, WaitMixin


_log = logging.getLogger(__name__)


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


def _internal_request(host: str) -> bool:
    address, _, _ = host.partition(":")
    try:
        ipaddress.ip_address(address)
    except ValueError:
        return address == "localhost"
    else:
        return True


@middleware
async def _healthcheck_middleware(
    request: Request, handler: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.path == "/_/health":
        host = request.headers.get("host")
        if not host or _internal_request(host):
            return Response(text="OK")
    return await handler(request)


@middleware
async def _opentracing_middleware(
    request: Request, handler: Callable[[Request], Awaitable[Response]],
) -> Response:
    tracer = get_tracer(__name__)
    attach(extract(_headers_getter, request))
    with tracer.start_as_current_span(
        request.path,
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

    .. wire:: harness.wires.aiohttp.web.ServerWire
      :type: output
      :runtime: python
      :config: harness.http.Server
      :requirements: aiohttp[speedups]

    """

    _runner: AppRunner
    _site: TCPSite
    _site_factory: Callable[[], TCPSite]

    def __init__(
        self, app: Application, *, access_log: Optional[Logger] = None,
    ) -> None:
        """
        :param app: configured :py:class:`aiohttp:aiohttp.web.Application`
            to run
        :param access_log: enable access logs by providing a logger instance
        """
        self._app = app
        self._access_log = access_log

    def configure(self, value: http_pb2.Server):
        assert isinstance(value, http_pb2.Server), type(value)

        self._app.middlewares.append(_healthcheck_middleware)
        self._app.middlewares.append(_opentracing_middleware)
        self._runner = AppRunner(self._app, access_log=self._access_log)
        self._site_factory = lambda: TCPSite(
            self._runner, value.bind.host, value.bind.port,
        )

    async def __aenter__(self):
        await self._runner.setup()
        self._site = self._site_factory()
        await self._site.start()
        _log.info("%s started: %s", self.__class__.__name__, self._site.name)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._runner.cleanup()
