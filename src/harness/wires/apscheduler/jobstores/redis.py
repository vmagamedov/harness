import logging

from apscheduler.jobstores.redis import RedisJobStore

from .... import redis_pb2

from ....wires.base import Wire


class RedisJobStoreWire(Wire):
    job_store: 'RedisJobStore'

    def configure(self, value: redis_pb2.Connection):
        self.job_store = RedisJobStore(
            db=value.db, host=value.address.host, port=value.address.port,
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.job_store.shutdown()
