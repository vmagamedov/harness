from grpclib.plugin.main import Buffer

from .types import Configuration, OutputFile


def _render_wires(cfg: Configuration):
    buf = Buffer()
    buf.add('# Generated by the Protocol Buffers compiler. DO NOT EDIT!')
    buf.add(f'# source: {cfg.proto_file}')
    buf.add(f'# plugin: {__name__}')
    buf.add('from dataclasses import dataclass')
    buf.add('')

    imports = set()
    for wire in cfg.inputs:
        module_name, _ = wire.path.rsplit('.', 1)
        imports.add(module_name)
    for wire in cfg.outputs:
        module_name, _ = wire.path.rsplit('.', 1)
        imports.add(module_name)
    for module_name in sorted(imports):
        buf.add(f'import {module_name}')
    buf.add('')

    pb2_module = cfg.proto_file.replace('/', '.').replace('.proto', '_pb2')
    buf.add(f'import {pb2_module}')
    buf.add('')
    buf.add('')

    buf.add('@dataclass')
    buf.add(f'class WiresIn:')
    with buf.indent():
        buf.add(f'config: {pb2_module}.Configuration')
        for wire_in in cfg.inputs:
            buf.add(f'{wire_in.name}: {wire_in.path}')
    buf.add('')
    buf.add('')
    buf.add('@dataclass')
    buf.add(f'class WiresOut:')
    with buf.indent():
        for wire_out in cfg.outputs:
            buf.add(f'{wire_out.name}: {wire_out.path}')
        if not cfg.outputs:
            buf.add('pass')
    file_name = cfg.proto_file.replace('.proto', '_wires.py')
    return OutputFile(name=file_name, content=buf.content())


def _render_entrypoint(cfg: Configuration):
    buf = Buffer()
    buf.add('# Generated by the Protocol Buffers compiler. DO NOT EDIT!')
    buf.add(f'# source: {cfg.proto_file}')
    buf.add(f'# plugin: {__name__}')
    buf.add('import sys')
    buf.add('')
    buf.add('from harness.runtime import Runner')
    buf.add('')

    main_module = cfg.proto_file.replace('/', '.').replace('.proto', '')
    pb2_module = cfg.proto_file.replace('/', '.').replace('.proto', '_pb2')
    wires_module = cfg.proto_file.replace('/', '.').replace('.proto', '_wires')

    buf.add(f'import {main_module}')
    buf.add(f'import {pb2_module}')
    buf.add(f'import {wires_module}')
    buf.add('')
    buf.add('runner = Runner(')
    buf.add(f'    {pb2_module}.Configuration,')
    buf.add(f'    {wires_module}.WiresIn,')
    buf.add(f'    {wires_module}.WiresOut,')
    buf.add(')')
    buf.add('')
    buf.add("if __name__ == '__main__':")
    with buf.indent():
        buf.add(f'sys.exit(runner.run({main_module}.main, sys.argv))')
    return OutputFile(name='entrypoint.py', content=buf.content())


def render(cfg: Configuration):
    yield _render_wires(cfg)
    yield _render_entrypoint(cfg)
