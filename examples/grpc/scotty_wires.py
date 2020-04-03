# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: scotty.proto
# plugin: harness.plugin.python
from typing import Optional
from dataclasses import dataclass

import harness.wires.asyncpg
import harness.wires.grpclib.server
import harness.wires.logging
import harness.wires.opentelemetry.ext.jaeger
import harness.wires.opentelemetry.ext.prometheus


@dataclass
class WiresIn:
    db: harness.wires.asyncpg.PoolWire
    console: Optional[harness.wires.logging.ConsoleWire]
    syslog: Optional[harness.wires.logging.SyslogWire]
    tracing: Optional[harness.wires.opentelemetry.ext.jaeger.JaegerSpanExporterWire]


@dataclass
class WiresOut:
    server: harness.wires.grpclib.server.ServerWire
    prometheus: harness.wires.opentelemetry.ext.prometheus.PrometheusMetricsExporterWire