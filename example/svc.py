from grpclib.server import Stream
from google.protobuf.empty_pb2 import Empty
from harness.resources.grpclib.v1 import Server

from svc_grpc import ExampleBase
from svc_wires import WiresIn, WiresOut


class Service(ExampleBase):

    def __init__(self, *, db, taskqueue):
        self._db = db
        self._taskqueue = taskqueue

    async def Store(self, stream: Stream[Empty, Empty]) -> None:
        pass


async def main(wires_in: WiresIn) -> WiresOut:
    print(wires_in.db.connection)
    print(wires_in.taskqueue.channel)
    return WiresOut(listen=Server([
        Service(db=wires_in.db, taskqueue=wires_in.taskqueue),
    ]))
