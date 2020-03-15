import pathlib
import pkg_resources


def proto_path():
    wire_proto_path = pkg_resources.resource_filename("harness", "wire.proto")
    print(pathlib.Path(wire_proto_path).parent.parent)
