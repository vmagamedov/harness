import logging
from dataclasses import dataclass

import harness.wires.prometheus
import harness.wires.grpclib.server
from asyncpg.pool import Pool
from grpclib.server import Stream
from google.protobuf.empty_pb2 import Empty

from scotty_grpc import ScottyBase
from scotty_wires import WiresIn, WiresOut


log = logging.getLogger(__name__)


@dataclass
class Scotty(ScottyBase):
    db: Pool

    async def BeamMeUp(self, stream: Stream[Empty, Empty]) -> None:
        await stream.recv_message()
        result = await self.db.fetchval('SELECT $1;', '42')
        assert result == '42', result
        await stream.send_message(Empty())


async def main(wires_in: WiresIn) -> WiresOut:
    log.info('Environment loaded')
    scotty = Scotty(
        db=wires_in.db.pool,
    )
    return WiresOut(
        server=harness.wires.grpclib.server.ServerWire([scotty]),
        prometheus=harness.wires.prometheus.ServerWire(),
    )
