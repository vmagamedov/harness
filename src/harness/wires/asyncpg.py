from asyncpg import Connection, create_pool
from asyncpg.pool import Pool
from opentelemetry.trace import get_tracer, SpanKind

from .. import postgres_pb2
from .base import Wire


def _wrap_do_execute(fn):
    async def _do_execute(self, query, executor, timeout, retry=True):
        if query.startswith(("SELECT ", "select ")):
            operation_name = "SELECT"
        elif query.startswith(("UPDATE ", "update ")):
            operation_name = "UPDATE"
        elif query.startswith(("INSERT ", "insert ")):
            operation_name = "INSERT"
        else:
            operation_name = "SQL"
        statement = " ".join(line.strip() for line in query.splitlines())
        with get_tracer(__name__).start_span(
            operation_name, kind=SpanKind.CLIENT,
        ) as span:
            span.set_attribute("component", "sql")
            span.set_attribute("sql.statement", statement)
            return await fn(self, query, executor, timeout, retry)

    _do_execute.__wrapped__ = True
    return _do_execute


class PoolWire(Wire):
    """

    .. wire:: harness.wires.asyncpg.PoolWire
      :type: input
      :runtime: python
      :config: harness.postgres.Pool
      :requirements: asyncpg

    """

    pool: Pool
    _connect = None
    _connect_params = None

    def configure(self, value: postgres_pb2.Pool):
        assert isinstance(value, postgres_pb2.Pool), type(value)

        self.pool = create_pool(
            host=value.address.host,
            port=value.address.port,
            user=value.username,
            password=value.password,
            database=value.database,
            min_size=value.min_size,
            max_size=value.max_size or 10,
        )

        if not getattr(Connection._do_execute, "__wrapped__", False):
            Connection._do_execute = _wrap_do_execute(Connection._do_execute)

    async def __aenter__(self):
        await self.pool.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pool.__aexit__(exc_type, exc_val, exc_tb)
