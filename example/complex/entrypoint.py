# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: spock/service.proto
# plugin: harness.plugin.main
import sys

from harness.runtime import Runner

import spock.service
import spock.service_pb2
import spock.service_wires

runner = Runner(
    spock.service_pb2.Configuration,
    spock.service_wires.WiresIn,
    spock.service_wires.WiresOut,
)

if __name__ == '__main__':
    sys.exit(runner.run(spock.service.main, sys.argv))
