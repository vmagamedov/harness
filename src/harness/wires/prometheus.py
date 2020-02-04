"""
    prometheus
    ==========

    Wires for the prometheus_client_ project.

    .. _prometheus_client: https://github.com/prometheus/client_python
"""
from .. import http_pb2

from .base import Wire, WaitMixin


class ServerWire(WaitMixin, Wire):
    _host = None
    _port = None
    _start = None

    def configure(self, value: http_pb2.Server):
        from prometheus_client import start_http_server

        if value.bind.port:
            self._host = value.bind.host or '0.0.0.0'
            self._port = value.bind.port
            self._start = start_http_server

    async def __aenter__(self):
        if self._port is not None:
            self._start(self._port, self._host)
            print(f'Metrics are exposed on {self._host}:{self._port}')
