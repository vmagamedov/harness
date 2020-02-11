import os
import sys

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse

from harness.wire_pb2 import HarnessWire, HarnessService

from . import python
from .types import Configuration, WireIn, WireOut


RUNTIMES = {
    'python': python.render,
}


class ConfigurationError(ValueError):
    pass


def process_file(proto_file, response, params):
    for config_message in proto_file.message_type:
        if config_message.name == 'Configuration':
            break
    else:
        raise ConfigurationError('Missing configuration message')

    inputs = []
    outputs = []
    for field in config_message.field:
        for _, option in field.options.ListFields():
            if not isinstance(option, HarnessWire):
                continue
            if option.WhichOneof('type') == 'input':
                inputs.append(WireIn(field.name, option.input))
            elif option.WhichOneof('type') == 'output':
                outputs.append(WireOut(field.name, option.output))
            else:
                continue

    if 'runtime' not in params:
        raise ConfigurationError('Runtime parameter is not specified')
    runtime = params['runtime']
    if runtime not in RUNTIMES:
        raise ConfigurationError(f'Unknown runtime: {runtime}')
    render = RUNTIMES[runtime]

    cfg = Configuration(
        proto_file=proto_file.name,
        inputs=inputs,
        outputs=outputs,
    )
    for file in render(cfg):
        gen_file = response.file.add()
        gen_file.name = file.name
        gen_file.content = file.content


def main() -> None:
    with os.fdopen(sys.stdin.fileno(), 'rb') as inp:
        request = CodeGeneratorRequest.FromString(inp.read())

    params = {}
    for pair in request.parameter.split(','):
        key, _, value = pair.partition('=')
        params[key] = value

    files_to_generate = set(request.file_to_generate)

    response = CodeGeneratorResponse()
    for pf in request.proto_file:
        if pf.name in files_to_generate:
            process_file(pf, response, params)

    with os.fdopen(sys.stdout.fileno(), 'wb') as out:
        out.write(response.SerializeToString())
