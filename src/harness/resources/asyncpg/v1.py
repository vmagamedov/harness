import harness.postgres_pb2

from ..base import Resource


class Connection(Resource):
    _dsn = None
    _connector = None
    connection = None

    def configure(self, value: harness.postgres_pb2.DSN):
        assert isinstance(value, harness.postgres_pb2.DSN), type(value)

        from asyncpg import connect

        assert value.value
        self._dsn = value.value
        self._connector = connect

    async def __aenter__(self):
        self.connection = await self._connector(self._dsn)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            await self.connection.close()
