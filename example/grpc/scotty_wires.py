# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: scotty.proto
# plugin: harness.cli.generate
from dataclasses import dataclass

import harness.wires.asyncpg
import harness.wires.grpclib
import harness.wires.logging
import harness.wires.opentelemetry.ext.jaeger
import harness.wires.prometheus

from scotty_pb2 import Configuration


@dataclass
class WiresOut:
    server: harness.wires.grpclib.ServerWire
    prometheus: harness.wires.prometheus.ServerWire


@dataclass
class WiresIn:
    __config__: Configuration
    __wires_out_type__ = WiresOut
    db: harness.wires.asyncpg.ConnectionWire
    console: harness.wires.logging.ConsoleWire
    syslog: harness.wires.logging.SyslogWire
    tracing: harness.wires.opentelemetry.ext.jaeger.JaegerSpanExporterWire