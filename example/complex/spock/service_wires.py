# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: spock/service.proto
# plugin: harness.plugin.main
from dataclasses import dataclass

import harness.wires.logging

import spock.service_pb2


@dataclass
class WiresIn:
    config: spock.service_pb2.Configuration
    console: harness.wires.logging.ConsoleWire


@dataclass
class WiresOut:
    pass
