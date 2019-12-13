from typing import List, Any
from typing_extensions import Protocol

import harness.grpc_pb2

from ..base import Wire


class _IServable(Protocol):
    def __mapping__(self) -> Any: ...


class Channel(Wire):
    channel = None

    def configure(self, value: harness.grpc_pb2.Channel):
        assert isinstance(value, harness.grpc_pb2.Channel), type(value)

        from grpclib.client import Channel

        self.channel = Channel(value.host or 'localhost',
                               value.port or 50051)

    async def __aenter__(self):
        return self.channel

    def close(self):
        self.channel.close()


class Server(Wire):
    _host = None
    _port = None
    server = None

    def __init__(self, handlers: List[_IServable]):
        self.handlers = handlers

    def configure(self, value: harness.grpc_pb2.Endpoint):
        assert isinstance(value, harness.grpc_pb2.Endpoint), type(value)

        from grpclib.server import Server
        from grpclib.reflection.service import ServerReflection

        self._host = value.host or '127.0.0.1'
        self._port = value.port or 50051

        handlers = list(self.handlers)
        services = ServerReflection.extend(handlers)
        self.server = Server(services)

    async def __aenter__(self):
        await self.server.start(self._host, self._port)
        print(f'Started gRPC server and listening on {self._host}:{self._port}')

    def close(self):
        self.server.close()

    async def wait_closed(self):
        await self.server.wait_closed()
