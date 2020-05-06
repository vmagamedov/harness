import logging

from types import TracebackType
from typing import Callable, Awaitable, List, Optional, Type, TypeVar
from typing import TYPE_CHECKING
from logging import Logger

from aiohttp.web import Application, AppRunner, TCPSite, Request, Response
from aiohttp.web import HTTPException, middleware
from aiohttp.web_response import StreamResponse

from opentelemetry.trace import get_tracer, SpanKind
from opentelemetry.context import attach
from opentelemetry.propagators import extract
from opentelemetry.trace.status import Status

from ... import http_pb2

from .. import _utils
from ..base import Wire, WaitMixin


if TYPE_CHECKING:
    from typing_extensions import Protocol

    _RT = TypeVar("_RT", covariant=True)

    class _Callback(Protocol[_RT]):
        def __call__(self) -> _RT:
            ...


_log = logging.getLogger(__name__)


@middleware
async def _healthcheck_middleware(
    request: Request, handler: Callable[[Request], Awaitable[StreamResponse]],
) -> StreamResponse:
    if request.path == "/_/health":
        host = request.headers.get("host")
        if not host or _utils.is_internal_request(host):
            return Response(text="OK")
    return await handler(request)


def _headers_getter(request: Request, header_name: str) -> List[str]:
    return request.headers.getall(header_name, [])  # type: ignore


@middleware
async def _opentracing_middleware(
    request: Request, handler: Callable[[Request], Awaitable[StreamResponse]],
) -> StreamResponse:
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
            code = _utils.status_to_canonical_code(e.status)
            span.set_status(Status(code))
            span.set_attribute("http.status_text", e.reason)
            raise
        else:
            code = _utils.status_to_canonical_code(response.status)
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
    _site_factory: "_Callback[TCPSite]"

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

    def configure(self, value: http_pb2.Server) -> None:
        assert isinstance(value, http_pb2.Server), type(value)

        self._app.middlewares.append(_healthcheck_middleware)
        self._app.middlewares.append(_opentracing_middleware)
        self._runner = AppRunner(self._app, access_log=self._access_log)
        self._site_factory = lambda: TCPSite(
            self._runner, value.bind.host, value.bind.port,
        )

    async def __aenter__(self) -> None:
        await self._runner.setup()
        self._site = self._site_factory()
        await self._site.start()
        _log.info("%s started: %s", self.__class__.__name__, self._site.name)

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self._runner.cleanup()
