from aiohttp import web
from harness.wires.aiohttp.web import ServerWire

from status_pb2 import Configuration
from status_wires import WiresIn, WiresOut


async def index(request: web.Request) -> web.Response:
    return web.Response(text="OK")


async def setup(config: Configuration, wires_in: WiresIn) -> WiresOut:
    app = web.Application()
    app.router.add_get("/", index)
    return WiresOut(server=ServerWire(app))
