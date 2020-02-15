from typing import TYPE_CHECKING, List, Any
from contextvars import ContextVar

from opentelemetry.trace import tracer, SpanKind
from opentelemetry.propagators import extract

from grpclib.server import Server
from grpclib.events import listen, RecvRequest, SendTrailingMetadata
from grpclib.reflection.service import ServerReflection

from ... import grpc_pb2
from ..base import Wire

if TYPE_CHECKING:
    from typing_extensions import Protocol  # noqa

    class _Servable(Protocol):
        def __mapping__(self) -> Any: ...


def _metadata_getter(metadata, header_name: str) -> List[str]:
    return metadata.getall(header_name, [])


_server_span_ctx = ContextVar('server_span_ctx')


async def _recv_request(event: RecvRequest) -> None:
    tracer_ = tracer()
    parent_span = extract(_metadata_getter, event.metadata)
    span = tracer_.start_span(
        event.method_name,
        parent_span,
        kind=SpanKind.SERVER,
        attributes={
            "component": "grpc",
            "grpc.method": event.method_name,
        },
    )
    span_ctx = tracer_.use_span(span, True)
    span_ctx.__enter__()
    _server_span_ctx.set(span_ctx)


async def _send_trailing_metadata(event: SendTrailingMetadata) -> None:
    _server_span_ctx.get().__exit__(None, None, None)


class ServerWire(Wire):
    _host: str
    _port: int
    server: Server

    def __init__(self, handlers: List['_Servable']):
        self.handlers = handlers

    def configure(self, value: grpc_pb2.Server):
        assert isinstance(value, grpc_pb2.Server), type(value)

        self._host = value.bind.host
        self._port = value.bind.port

        handlers = list(self.handlers)
        services = ServerReflection.extend(handlers)
        self.server = Server(services)
        listen(self.server, RecvRequest, _recv_request)
        listen(self.server, SendTrailingMetadata, _send_trailing_metadata)

    async def __aenter__(self):
        await self.server.start(self._host, self._port)
        print(f'Started gRPC server and listening on {self._host}:{self._port}')

    def close(self):
        self.server.close()

    async def wait_closed(self):
        await self.server.wait_closed()
