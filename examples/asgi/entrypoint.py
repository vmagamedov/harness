# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: mccoy.proto
# plugin: harness.plugin.python
import sys

from harness.runtime import Runner

import mccoy
import mccoy_pb2
import mccoy_wires

runner = Runner(
    mccoy_pb2.Configuration,
    mccoy_wires.WiresIn,
    mccoy_wires.WiresOut,
)

if __name__ == '__main__':
    sys.exit(runner.run(mccoy.setup, sys.argv))
