from .. import postgres_pb2

from .base import Wire


class ConnectionWire(Wire):
    _connect = None
    _connect_params = None
    connection = None

    def configure(self, value: postgres_pb2.Connection):
        assert isinstance(value, postgres_pb2.Connection), type(value)

        from asyncpg import connect

        self._connect = connect
        self._connect_params = dict(
            host=value.address.host,
            port=value.address.port,
            user=value.username,
            password=value.password,
            database=value.database,
        )

    async def __aenter__(self):
        self.connection = await self._connect(**self._connect_params)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            await self.connection.close()
