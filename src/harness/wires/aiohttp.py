from typing import TYPE_CHECKING

from .. import http_pb2

from .base import Wire, WaitMixin

if TYPE_CHECKING:
    from aiohttp.web import Application


class ServerWire(WaitMixin, Wire):
    _runner = None
    _site = None
    _site_factory = None

    def __init__(self, app: 'Application', *, access_log=None):
        self._app = app
        self._access_log = access_log

    def configure(self, value: http_pb2.Server):
        assert isinstance(value, http_pb2.Server), type(value)

        from aiohttp.web_runner import AppRunner, TCPSite

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
