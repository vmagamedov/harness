"""
    apscheduler
    ===========

    Wires for the apscheduler_ project.

    .. _apscheduler: https://github.com/agronholm/apscheduler
"""
from apscheduler.schedulers.base import BaseScheduler

from ..base import Wire, WaitMixin


class SchedulerWire(WaitMixin, Wire):

    def __init__(self, scheduler: 'BaseScheduler'):
        self._scheduler = scheduler

    async def __aenter__(self):
        self._scheduler.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._scheduler.shutdown()
