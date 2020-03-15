import asyncio

from .. import net_pb2

from .base import Wire, WaitMixin


class MonitorWire(WaitMixin, Wire):
    """

    .. wire:: harness.wires.aiomonitor.MonitorWire
      :type: output
      :runtime: python
      :config: harness.net.Server
      :requirements: aiomonitor

    """

    _monitor = None

    def configure(self, value: net_pb2.Server):
        assert isinstance(value, net_pb2.Server), type(value)

        from aiomonitor import Monitor, MONITOR_HOST, MONITOR_PORT

        self._monitor = Monitor(
            loop=asyncio.get_event_loop(),
            host=value.bind.host or MONITOR_HOST,
            port=value.bind.port or MONITOR_PORT,
        )

    async def __aenter__(self):
        self._monitor.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._monitor.close()
