import os
import sys
from pprint import pprint
from collections import defaultdict

from pkg_resources import iter_entry_points

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse


EXT_NUMBER = 2001


def pp(*obj):
    pprint(obj[0] if len(obj) == 1 else obj, stream=sys.stderr)


def main() -> None:
    with os.fdopen(sys.stdin.fileno(), 'rb') as inp:
        request = CodeGeneratorRequest.FromString(inp.read())

    configurations = defaultdict(dict)

    for pf in request.proto_file:
        for mt in pf.message_type:
            for f in mt.field:
                for uf in f.options.UnknownFields():
                    if uf.field_number == EXT_NUMBER:
                        configurations[mt.name][f.name] = uf.data.decode('ascii')  # noqa

    module_keys = set()
    for c in configurations.values():
        module_keys.update(c.values())

    modules = set()
    resources = {}
    for entry_point in iter_entry_points(group='harness.wires', name=None):
        if entry_point.name in module_keys and entry_point.name not in modules:
            modules.add(entry_point.name)
            module = entry_point.load()
            for name, obj in module.__dict__.items():
                if hasattr(obj, '__implements__'):
                    resources[(entry_point.name, obj.__implements__)] = obj

    pp(resources)

    response = CodeGeneratorResponse()
    for file_to_generate in request.file_to_generate:
        file = response.file.add()
        file.name = file_to_generate.replace('.proto', '_wires.py')
        file.content = 'import math\n'

    with os.fdopen(sys.stdout.fileno(), 'wb') as out:
        out.write(response.SerializeToString())
