from typing import TYPE_CHECKING, List, Any, NewType, Union
from contextvars import ContextVar

from typing_extensions import Protocol

from opentelemetry.trace import tracer, SpanKind
from opentelemetry.propagators import extract

from grpclib.server import Server
from grpclib.client import Channel
from grpclib.events import RecvRequest, SendRequest, listen
from grpclib.events import RecvTrailingMetadata, SendTrailingMetadata
from grpclib.reflection.service import ServerReflection

from .. import grpc_pb2
from .base import Wire

if TYPE_CHECKING:
    from multidict import MultiDict  # noqa


class _IServable(Protocol):
    def __mapping__(self) -> Any: ...


_Value = Union[str, bytes]
_Metadata = NewType('_Metadata', 'MultiDict[_Value]')


async def _send_request(event: SendRequest) -> None:
    pass


async def _recv_trailing_metadata(event: RecvTrailingMetadata) -> None:
    pass


class ChannelWire(Wire):
    channel = None

    def configure(self, value: grpc_pb2.Channel):
        assert isinstance(value, grpc_pb2.Channel), type(value)

        self.channel = Channel(value.address.host or 'localhost',
                               value.address.port or 50051)
        listen(self.channel, SendRequest, _send_request)
        listen(self.channel, RecvTrailingMetadata, _recv_trailing_metadata)

    async def __aenter__(self):
        return self.channel

    def close(self):
        self.channel.close()


def _metadata_getter(metadata: _Metadata, header_name: str) -> List[str]:
    return metadata.getall(header_name, [])


_current_span = ContextVar('span')


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
    _current_span.set(span)


async def _send_trailing_metadata(event: SendTrailingMetadata) -> None:
    _current_span.get().end()


class ServerWire(Wire):
    _host = None
    _port = None
    server = None

    def __init__(self, handlers: List[_IServable]):
        self.handlers = handlers

    def configure(self, value: grpc_pb2.Server):
        assert isinstance(value, grpc_pb2.Server), type(value)

        self._host = value.bind.host or '127.0.0.1'
        self._port = value.bind.port or 50051

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
