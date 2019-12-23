from asyncio import Event

from .. import prometheus_pb2

from .base import Wire


class ServerWire(Wire):
    _host = None
    _port = None
    _start = None
    _exit = None

    def configure(self, value: prometheus_pb2.Endpoint):
        from prometheus_client import start_http_server

        if value.port:
            self._host = value.host or '0.0.0.0'
            self._port = value.port
            self._start = start_http_server

        self._exit = Event()

    async def __aenter__(self):
        if self._port is not None:
            self._start(self._port, self._host)
            print(f'Metrics are exposed on {self._host}:{self._port}')

    def close(self):
        self._exit.set()

    async def wait_closed(self):
        await self._exit.wait()
