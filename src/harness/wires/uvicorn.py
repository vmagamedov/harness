import socket
import logging
from typing import List, Dict

from opentelemetry.trace import get_tracer, SpanKind
from opentelemetry.context import attach
from opentelemetry.propagators import extract
from opentelemetry.trace.status import Status

from uvicorn import Config, Server

from .. import http_pb2

from . import _utils
from .base import Wire


_log = logging.getLogger(__name__)


def _healthcheck_middleware(app):
    async def ok(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"text/plain"]],
            }
        )
        await send({"type": "http.response.body", "body": b"OK"})

    async def middleware(scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/_/health":
            headers = dict(scope["headers"])
            host_bytes = headers.get(b"host")
            if host_bytes:
                host = host_bytes.decode("utf-8")
                if _utils.is_internal_request(host):
                    await ok(scope, receive, send)
                    return
            else:
                await ok(scope, receive, send)
                return
        await app(scope, receive, send)

    return middleware


def _metadata_getter(headers: Dict[bytes, bytes], header_name: str) -> List[str]:
    header_name_bytes = header_name.lower().encode("utf-8")
    value = headers.get(header_name_bytes)
    return [value] if value is not None else []


def _opentracing_middleware(app):
    async def middleware(scope, receive, send):
        if scope["type"] == "http":
            response = []

            async def send_hook(data):
                if data["type"] == "http.response.start":
                    response.append(data)
                await send(data)

            headers = dict(scope["headers"])
            host_bytes = headers.get(b"host")
            if host_bytes is None:
                host = socket.getfqdn()
            else:
                host = host_bytes.decode("utf-8")

            tracer = get_tracer(__name__)
            attach(extract(_metadata_getter, headers))
            with tracer.start_as_current_span(
                scope["path"],
                kind=SpanKind.SERVER,
                attributes={
                    "component": "http",
                    "http.method": scope["method"],
                    "http.scheme": scope.get("scheme", "http"),
                    "http.host": host,
                },
            ) as span:
                await app(scope, receive, send_hook)
                if response:
                    status = response[0]["status"]
                    code = _utils.status_to_canonical_code(status)
                    span.set_status(Status(code))
        else:
            await app(scope, receive, send)

    return middleware


class ServerWire(Wire):
    """

    .. wire:: harness.wires.uvicorn.ServerWire
      :type: output
      :runtime: python
      :config: harness.http.Server
      :requirements: uvicorn

    """

    server: Server

    def __init__(self, app):
        self._app = app

    def configure(self, value: http_pb2.Server):
        assert isinstance(value, http_pb2.Server), type(value)
        app = _healthcheck_middleware(self._app)
        app = _opentracing_middleware(app)
        config = Config(
            app, value.bind.host, value.bind.port, log_config=None, access_log=False,
        )
        self.server = Server(config)
        logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

    async def __aenter__(self):
        config = self.server.config
        config.load()
        self.server.lifespan = config.lifespan_class(config)
        await self.server.startup()
        _log.info(
            "%s started: addr=%s:%d", self.__class__.__name__, config.host, config.port,
        )

    def close(self) -> None:
        self.server.should_exit = True

    async def wait_closed(self) -> None:
        await self.server.main_loop()
        await self.server.shutdown()
