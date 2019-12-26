from typing import TYPE_CHECKING

from .. import redis_pb2
from .base import Wire, WaitMixin

if TYPE_CHECKING:
    from apscheduler.schedulers.base import BaseScheduler
    from apscheduler.jobstores.redis import RedisJobStore


class SchedulerWire(WaitMixin, Wire):

    def __init__(self, scheduler: 'BaseScheduler'):
        self._scheduler = scheduler

    async def __aenter__(self):
        self._scheduler.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._scheduler.shutdown()


class RedisJobStoreWire(Wire):
    job_store: 'RedisJobStore'

    def configure(self, value: redis_pb2.Connection):
        from apscheduler.jobstores.redis import RedisJobStore

        self.job_store = RedisJobStore(
            db=value.db, host=value.address.host, port=value.address.port,
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.job_store.shutdown()
