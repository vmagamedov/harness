from aiohttp import web
from google.protobuf.empty_pb2 import Empty

from harness.wires.aiohttp import ServerWire
from harness.wires.aiomonitor import MonitorWire

from scotty_grpc import ScottyStub

from kirk_wires import WiresIn, WiresOut


async def index(request):
    now = await request.app['db'].fetchval('SELECT now();')
    await request.app['scotty'].BeamMeUp(Empty())
    version = await request.app['db'].fetchval('SELECT version();')
    return web.Response(text=f'Time: {now}\nPG Version: {version}\n')


async def main(wires_in: WiresIn) -> WiresOut:
    app = web.Application()
    app.router.add_get('/', index)
    app['db'] = wires_in.db.pool
    app['scotty'] = ScottyStub(wires_in.scotty.channel)
    return WiresOut(server=ServerWire(app),
                    monitor=MonitorWire())
