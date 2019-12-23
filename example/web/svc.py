from aiohttp import web
from harness.wires.aiohttp import ServerWire

from svc_wires import WiresIn, WiresOut


async def hello(request):
    return web.Response(text='Hello World!')


async def main(wires_in: WiresIn) -> WiresOut:
    app = web.Application()
    app.router.add_get('/', hello)
    app['db'] = wires_in.db.connection
    return WiresOut(listen=ServerWire(app))
