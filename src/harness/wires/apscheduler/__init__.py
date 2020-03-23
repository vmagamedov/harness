from apscheduler.schedulers.base import BaseScheduler

from ..base import Wire, WaitMixin


class SchedulerWire(WaitMixin, Wire):
    """

    .. wire:: harness.wires.apscheduler.SchedulerWire
      :type: output
      :runtime: python
      :config: google.protobuf.Empty
      :requirements: apscheduler

    """

    def __init__(self, scheduler: BaseScheduler):
        self._scheduler = scheduler

    async def __aenter__(self):
        self._scheduler.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._scheduler.shutdown()
