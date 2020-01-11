import logging

from harness.wires.apscheduler import SchedulerWire
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kirk_wires import WiresIn, WiresOut


async def tick():
    logging.info('Tick')


async def main(wires_in: WiresIn) -> WiresOut:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tick, 'interval', seconds=5)
    scheduler.configure(jobstores={
        'default': wires_in.redis_job_store.job_store,
    })
    return WiresOut(scheduler=SchedulerWire(scheduler=scheduler))
