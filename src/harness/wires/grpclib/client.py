from contextvars import ContextVar

from opentelemetry.trace import get_tracer, SpanKind
from opentelemetry.propagators import inject

from grpclib.client import Channel
from grpclib.events import listen, SendRequest, RecvTrailingMetadata

from harness import grpc_pb2
from harness.wires.base import Wire


_client_span = ContextVar("client_span")


async def _send_request(event: SendRequest) -> None:
    tracer = get_tracer(__name__)
    span = tracer.start_span(
        event.method_name,
        kind=SpanKind.CLIENT,
        attributes={"component": "grpc", "grpc.method": event.method_name},
    )
    _client_span.set(span)
    inject(type(event.metadata).__setitem__, event.metadata)


async def _recv_trailing_metadata(event: RecvTrailingMetadata) -> None:
    _client_span.get().end()


class ChannelWire(Wire):
    """

    .. wire:: harness.wires.grpclib.client.ChannelWire
      :type: input
      :runtime: python
      :config: harness.grpc.Channel
      :requirements:
        grpclib
        protobuf

    """

    channel: Channel

    def configure(self, value: grpc_pb2.Channel):
        assert isinstance(value, grpc_pb2.Channel), type(value)

        self.channel = Channel(value.address.host, value.address.port)
        listen(self.channel, SendRequest, _send_request)
        listen(self.channel, RecvTrailingMetadata, _recv_trailing_metadata)

    def close(self):
        self.channel.close()
