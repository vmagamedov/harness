import logging

from uvicorn import Config, Server

from .. import http_pb2

from .base import Wire


_log = logging.getLogger(__name__)


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
        config = Config(
            self._app,
            value.bind.host,
            value.bind.port,
            log_config=None,
            access_log=False,
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
