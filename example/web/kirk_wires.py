# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: kirk.proto
# plugin: harness.plugin.main
from dataclasses import dataclass

import harness.wires.aiohttp
import harness.wires.aiomonitor
import harness.wires.asyncpg
import harness.wires.grpclib
import harness.wires.logging
import harness.wires.opentelemetry.ext.jaeger

from kirk_pb2 import Configuration


@dataclass
class WiresOut:
    server: harness.wires.aiohttp.ServerWire
    monitor: harness.wires.aiomonitor.MonitorWire


@dataclass
class WiresIn:
    __config__: Configuration
    __wires_out_type__ = WiresOut
    db: harness.wires.asyncpg.PoolWire
    scotty: harness.wires.grpclib.ChannelWire
    console: harness.wires.logging.ConsoleWire
    tracing: harness.wires.opentelemetry.ext.jaeger.JaegerSpanExporterWire
