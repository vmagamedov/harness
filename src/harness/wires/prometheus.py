import logging

from prometheus_client import start_http_server

from .. import http_pb2

from .base import Wire, WaitMixin


_log = logging.getLogger(__name__)


class ServerWire(WaitMixin, Wire):
    """

    .. wire:: harness.wires.prometheus.ServerWire
      :type: output
      :runtime: python
      :config: harness.http.Server
      :requirements: prometheus_client

    """

    _config: http_pb2.Server

    def configure(self, value: http_pb2.Server):
        assert isinstance(value, http_pb2.Server), type(value)
        self._config = value

    async def __aenter__(self):
        start_http_server(self._config.bind.port, self._config.bind.host)
        _log.info(
            "%s started: addr=%s:%d",
            self.__class__.__name__,
            self._config.bind.host,
            self._config.bind.port,
        )
