import os
import sys

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse

from harness.wire_pb2 import HarnessWire, HarnessService

from . import python
from .types import Context, WireIn, WireOut


LANGUAGES = {
    'python': HarnessService.PYTHON,
}

RENDERER = {
    HarnessService.PYTHON: python.render,
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

    if 'language' in params:
        params_language = params['language']
        if params_language not in LANGUAGES:
            raise ConfigurationError(f'Unknown language specified in the '
                                     f'command-line: {params_language}')
        else:
            language = LANGUAGES[params_language]
    else:
        language = None
        for _, option in config_message.options.ListFields():
            if not isinstance(option, HarnessService):
                continue
            language = option.language
        if not language:
            raise ConfigurationError('Language is not specified')

    ctx = Context(
        proto_file=proto_file.name,
        inputs=inputs,
        outputs=outputs,
    )
    renderer = RENDERER[language]
    for file in renderer(ctx):
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
