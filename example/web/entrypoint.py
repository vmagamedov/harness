# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: kirk.proto
# plugin: harness.plugin.main
import sys

from harness.runtime import Runner

import kirk
import kirk_pb2
import kirk_wires

runner = Runner(
    kirk_pb2.Configuration,
    kirk_wires.WiresIn,
    kirk_wires.WiresOut,
)

if __name__ == '__main__':
    sys.exit(runner.run(kirk.main, sys.argv))
