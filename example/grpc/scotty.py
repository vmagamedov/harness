import logging
from dataclasses import dataclass

import asyncpg
import harness.wires.grpclib
import harness.wires.prometheus
from grpclib.server import Stream
from google.protobuf.empty_pb2 import Empty

from scotty_grpc import ScottyBase
from scotty_wires import WiresIn, WiresOut


log = logging.getLogger(__name__)


@dataclass
class Scotty(ScottyBase):
    db: asyncpg.Connection

    async def BeamMeUp(self, stream: Stream[Empty, Empty]) -> None:
        request = await stream.recv_message()
        print(request)
        await stream.send_message(Empty())


async def main(wires_in: WiresIn) -> WiresOut:
    log.info('Environment loaded')
    scotty = Scotty(
        db=wires_in.db.connection,
    )
    return WiresOut(
        server=harness.wires.grpclib.ServerWire([scotty]),
        prometheus=harness.wires.prometheus.ServerWire(),
    )
