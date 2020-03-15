import asyncio


class Wire:
    def configure(self, value):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()
        await self.wait_closed()

    def close(self):
        pass

    async def wait_closed(self):
        pass


class WaitMixin:
    _event: asyncio.Event

    def close(self):
        if not hasattr(self, "_event"):
            self._event = asyncio.Event()
        self._event.set()

    async def wait_closed(self):
        if not hasattr(self, "_event"):
            self._event = asyncio.Event()
        await self._event.wait()
