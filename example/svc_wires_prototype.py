import asyncio
from typing import Callable, Awaitable
from contextlib import AsyncExitStack
from dataclasses import dataclass

import harness.runtime
import harness.resources.asyncpg.v1
import harness.resources.grpclib.v1

from svc_pb2 import Configuration


@dataclass
class WiresIn:
    __config__: Configuration

    db: harness.resources.asyncpg.v1.EngineResource
    taskqueue: harness.resources.grpclib.v1.ChannelResource

    @classmethod
    def __wrapper__(cls):
        return wrapper


@dataclass
class WiresOut:
    listen: harness.resources.grpclib.v1.ServerResource


async def wrapper(
    service: Callable[[WiresIn], Awaitable[WiresOut]],
    config: Configuration,
) -> None:
    async with AsyncExitStack() as stack:
        db_resource = harness.resources.asyncpg.v1.EngineResource()
        db_resource.configure(config.db)
        db = await stack.enter_async_context(db_resource)

        taskqueue_resource = harness.resources.grpclib.v1.ChannelResource()
        taskqueue_resource.configure(config.taskqueue)
        taskqueue = await stack.enter_async_context(taskqueue_resource)

        wires_in = WiresIn(
            __config__=config,
            db=db,
            taskqueue=taskqueue,
        )

        wires_out = await service(wires_in)

        wires_out.listen.configure(config.listen)
        await stack.enter_async_context(wires_out.listen)

        with harness.runtime.graceful_exit([wires_out.listen]):
            await asyncio.wait(
                {
                    wires_out.listen.wait_closed(),
                },
                return_when=asyncio.FIRST_COMPLETED,
            )
