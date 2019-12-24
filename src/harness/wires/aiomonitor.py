import asyncio

from .. import http_pb2

from .base import Wire, WaitMixin


class MonitorWire(WaitMixin, Wire):
    _monitor = None

    def configure(self, value: http_pb2.Server):
        assert isinstance(value, http_pb2.Server), type(value)

        from aiomonitor import Monitor, MONITOR_HOST, MONITOR_PORT

        type_ = value.WhichOneof('type')
        if not type_:
            self._monitor = Monitor(
                loop=asyncio.get_event_loop(),
            )
        elif type_ == 'tcp':
            self._monitor = Monitor(
                loop=asyncio.get_event_loop(),
                host=value.tcp.host or MONITOR_HOST,
                port=value.tcp.port or MONITOR_PORT,
            )
        else:
            raise NotImplementedError(type_)

    async def __aenter__(self):
        self._monitor.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._monitor.close()
