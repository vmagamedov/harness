from harness.wires.uvicorn import ServerWire

from mccoy_wires import WiresIn, WiresOut


async def app(scope, receive, send):
    assert scope["type"] == "http"
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/plain"]],
        }
    )
    await send({"type": "http.response.body", "body": b"Hello, world!"})


async def setup(config, wires_in: WiresIn) -> WiresOut:
    return WiresOut(server=ServerWire(app))
