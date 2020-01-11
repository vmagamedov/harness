from aiohttp import web
from google.protobuf.empty_pb2 import Empty

from harness.wires.aiohttp import ServerWire
from harness.wires.aiomonitor import MonitorWire

from scotty_grpc import ScottyStub

from kirk_wires import WiresIn, WiresOut


async def index(request):
    reply = await request.app['scotty'].BeamMeUp(Empty())
    return web.Response(text=f'Scotty: {reply}')


async def main(wires_in: WiresIn) -> WiresOut:
    app = web.Application()
    app.router.add_get('/', index)
    app['db'] = wires_in.db.connection
    app['scotty'] = ScottyStub(wires_in.scotty.channel)
    return WiresOut(server=ServerWire(app),
                    monitor=MonitorWire())
