from grpclib.server import Stream
from google.protobuf.empty_pb2 import Empty
from harness.resources.grpclib.v1 import ServerResource

from svc_grpc import ExampleBase
from svc_wires_prototype import WiresIn, WiresOut


class Service(ExampleBase):

    def __init__(self, *, db, taskqueue):
        self._db = db
        self._taskqueue = taskqueue

    async def Store(self, stream: Stream[Empty, Empty]) -> None:
        pass


async def main(wires_in: WiresIn) -> WiresOut:
    print(wires_in)
    return WiresOut(listen=ServerResource([
        Service(db=wires_in.db, taskqueue=wires_in.taskqueue),
    ]))
