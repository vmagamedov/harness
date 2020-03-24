import logging
from typing import TYPE_CHECKING, List, Any
from contextvars import ContextVar

from opentelemetry.trace import get_tracer, SpanKind
from opentelemetry.context import attach
from opentelemetry.propagators import extract

from grpclib.server import Server
from grpclib.events import listen, RecvRequest, SendTrailingMetadata
from grpclib.health.service import Health
from grpclib.reflection.service import ServerReflection

from ... import grpc_pb2
from ..base import Wire

if TYPE_CHECKING:
    from typing_extensions import Protocol

    class _Servable(Protocol):
        def __mapping__(self) -> Any:
            ...


_log = logging.getLogger(__name__)


def _metadata_getter(metadata, header_name: str) -> List[str]:
    return metadata.getall(header_name, [])


_server_span_ctx = ContextVar("server_span_ctx")


async def _recv_request(event: RecvRequest) -> None:
    tracer = get_tracer(__name__)
    attach(extract(_metadata_getter, event.metadata))
    span_ctx = tracer.start_as_current_span(
        event.method_name,
        kind=SpanKind.SERVER,
        attributes={"component": "grpc", "grpc.method": event.method_name},
    )
    span_ctx.__enter__()
    _server_span_ctx.set(span_ctx)


async def _send_trailing_metadata(event: SendTrailingMetadata) -> None:
    _server_span_ctx.get().__exit__(None, None, None)


class ServerWire(Wire):
    """

    .. wire:: harness.wires.grpclib.server.ServerWire
      :type: output
      :runtime: python
      :config: harness.grpc.Server
      :requirements:
        grpclib
        protobuf

    """

    _config: grpc_pb2.Server
    server: Server

    def __init__(self, handlers: List["_Servable"]):
        self.handlers = handlers

    def configure(self, value: grpc_pb2.Server):
        assert isinstance(value, grpc_pb2.Server), type(value)
        self._config = value

        handlers = list(self.handlers)
        if not any(isinstance(h, Health) for h in handlers):
            handlers.append(Health())
        handlers = ServerReflection.extend(handlers)

        self.server = Server(handlers)
        listen(self.server, RecvRequest, _recv_request)
        listen(self.server, SendTrailingMetadata, _send_trailing_metadata)

    async def __aenter__(self):
        await self.server.start(self._config.bind.host, self._config.bind.port)
        _log.info(
            "%s started: addr=%s:%d",
            self.__class__.__name__,
            self._config.bind.host,
            self._config.bind.port,
        )

    def close(self):
        self.server.close()

    async def wait_closed(self):
        await self.server.wait_closed()
