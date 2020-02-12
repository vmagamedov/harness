import os
import sys

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse

from ..config import translate_descriptor_proto

from . import python


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

    if 'runtime' not in params:
        raise ConfigurationError('Runtime parameter is not specified')
    runtime = params['runtime']
    if runtime not in RUNTIMES:
        raise ConfigurationError(f'Unknown runtime: {runtime}')
    render = RUNTIMES[runtime]

    config_spec = translate_descriptor_proto(config_message)
    for name, content in render(proto_file.name, config_spec):
        f = response.file.add()
        f.name = name
        f.content = content


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
