import logging

from uvicorn import Config, Server
from opentelemetry.ext.asgi import OpenTelemetryMiddleware

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


class ServerWire(Wire):
    """

    .. wire:: harness.wires.uvicorn.ServerWire
      :type: output
      :runtime: python
      :config: harness.http.Server
      :requirements:
        uvicorn
        opentelemetry-ext-asgi

    """

    server: Server

    def __init__(self, app):
        self._app = app

    def configure(self, value: http_pb2.Server):
        assert isinstance(value, http_pb2.Server), type(value)
        app = _healthcheck_middleware(self._app)
        app = OpenTelemetryMiddleware(app)
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
