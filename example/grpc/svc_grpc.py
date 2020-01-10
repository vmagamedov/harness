# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: svc.proto
# plugin: grpclib.plugin.main
import abc
import typing

import grpclib.const
import grpclib.client
if typing.TYPE_CHECKING:
    import grpclib.server

import harness.wire_pb2
import harness.postgres_pb2
import harness.grpc_pb2
import harness.logging_pb2
import harness.http_pb2
import harness.tracing_pb2
import google.protobuf.empty_pb2
import svc_pb2


class ExampleBase(abc.ABC):

    @abc.abstractmethod
    async def Store(self, stream: 'grpclib.server.Stream[google.protobuf.empty_pb2.Empty, google.protobuf.empty_pb2.Empty]') -> None:
        pass

    def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:
        return {
            '/example.Example/Store': grpclib.const.Handler(
                self.Store,
                grpclib.const.Cardinality.UNARY_UNARY,
                google.protobuf.empty_pb2.Empty,
                google.protobuf.empty_pb2.Empty,
            ),
        }


class ExampleStub:

    def __init__(self, channel: grpclib.client.Channel) -> None:
        self.Store = grpclib.client.UnaryUnaryMethod(
            channel,
            '/example.Example/Store',
            google.protobuf.empty_pb2.Empty,
            google.protobuf.empty_pb2.Empty,
        )
