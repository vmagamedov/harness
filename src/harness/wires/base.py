import asyncio
from types import TracebackType
from typing import Optional, Type, Any


class Wire:
    def configure(self, value: Any) -> None:
        pass

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()
        await self.wait_closed()

    def close(self) -> None:
        pass

    async def wait_closed(self) -> None:
        pass


class WaitMixin:
    _event: asyncio.Event

    def close(self) -> None:
        if not hasattr(self, "_event"):
            self._event = asyncio.Event()
        self._event.set()

    async def wait_closed(self) -> None:
        if not hasattr(self, "_event"):
            self._event = asyncio.Event()
        await self._event.wait()
