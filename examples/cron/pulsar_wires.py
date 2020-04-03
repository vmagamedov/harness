# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: pulsar.proto
# plugin: harness.plugin.python
from dataclasses import dataclass

import harness.wires.apscheduler
import harness.wires.apscheduler.jobstores.redis
import harness.wires.logging


@dataclass
class WiresIn:
    redis_job_store: harness.wires.apscheduler.jobstores.redis.RedisJobStoreWire
    console: harness.wires.logging.ConsoleWire


@dataclass
class WiresOut:
    scheduler: harness.wires.apscheduler.SchedulerWire