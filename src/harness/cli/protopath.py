import pathlib
import pkg_resources


def proto_path(args):
    wire_proto_path = pkg_resources.resource_filename('harness', 'wire.proto')
    print(pathlib.Path(wire_proto_path).parent.parent)


def add_commands(subparsers):
    check_parser = subparsers.add_parser('proto-path')
    check_parser.set_defaults(func=proto_path)
