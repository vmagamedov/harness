import logging
from dataclasses import dataclass

import asyncpg
import grpclib.client
from grpclib.server import Stream
from harness.wires.grpclib import Server
from harness.wires.prometheus import Server as PServer
from google.protobuf.empty_pb2 import Empty

from svc_grpc import ExampleBase
from svc_wires import WiresIn, WiresOut


log = logging.getLogger(__name__)


@dataclass
class Service(ExampleBase):
    db: asyncpg.Connection
    taskqueue: grpclib.client.Channel

    async def Store(self, stream: Stream[Empty, Empty]) -> None:
        request = await stream.recv_message()
        print(request)
        await stream.send_message(Empty())


async def main(wires_in: WiresIn) -> WiresOut:
    log.info('Environment loaded')
    service = Service(
        db=wires_in.db.connection,
        taskqueue=wires_in.taskqueue.channel,
    )
    return WiresOut(listen=Server([service]),
                    prometheus=PServer())
