import os
import sys
from typing import Collection, List, Dict
from dataclasses import dataclass

from pkg_resources import iter_entry_points, EntryPoint

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse

from grpclib.plugin.main import Buffer


INPUT_EXT_NUMBER = 2001
OUTPUT_EXT_NUMBER = 2002

ProtoFile = str
MessageName = str
FieldName = str
ResourcePath = str


@dataclass
class ResourceContext:
    field_name: FieldName
    resource_path: ResourcePath


@dataclass
class ConfigurationContext:
    class_name: MessageName
    wires_in_name: str
    wires_out_name: str
    inputs: Collection[ResourceContext]
    outputs: Collection[ResourceContext]


@dataclass
class ModuleContext:
    proto_file: ProtoFile
    adapter_imports: Collection[str]
    pb2_module: str
    configurations: Collection[ConfigurationContext]


def main() -> None:
    with os.fdopen(sys.stdin.fileno(), 'rb') as inp:
        request = CodeGeneratorRequest.FromString(inp.read())

    files_to_generate = set(request.file_to_generate)

    entrypoints: Dict[str, EntryPoint] = {
        entry_point.name: entry_point
        for entry_point in iter_entry_points(group='harness.wires', name=None)
    }

    response = CodeGeneratorResponse()
    for pf in request.proto_file:
        if pf.name not in files_to_generate:
            continue

        configurations = []
        adapter_imports = set()
        pb2_module = pf.name.replace('/', '.').replace('.proto', '_pb2')

        for mt in pf.message_type:
            inputs: List[ResourceContext] = []
            outputs: List[ResourceContext] = []
            for f in mt.field:
                for uf in f.options.UnknownFields():
                    if uf.field_number == INPUT_EXT_NUMBER:
                        collection = inputs
                    elif uf.field_number == OUTPUT_EXT_NUMBER:
                        collection = outputs
                    else:
                        continue
                    assert f.type_name
                    option_value = uf.data.decode('ascii')
                    adapter_name, _, resource_name = option_value.partition(':')
                    adapter_path = entrypoints[adapter_name].module_name
                    resource_path = f'{adapter_path}.{resource_name}'
                    collection.append(ResourceContext(
                        field_name=f.name,
                        resource_path=resource_path,
                    ))
                    adapter_imports.add(adapter_path)
            if inputs or outputs:
                config_ctx = ConfigurationContext(
                    class_name=mt.name,
                    wires_in_name='WiresIn',
                    wires_out_name='WiresOut',
                    inputs=inputs,
                    outputs=outputs,
                )
                configurations.append(config_ctx)
        module_ctx = ModuleContext(
            proto_file=pf.name,
            adapter_imports=sorted(adapter_imports),
            pb2_module=pb2_module,
            configurations=configurations,
        )
        file = response.file.add()
        file.name = pf.name.replace('.proto', '_wires.py')
        file.content = render(module_ctx)

    with os.fdopen(sys.stdout.fileno(), 'wb') as out:
        out.write(response.SerializeToString())


def render(ctx: ModuleContext) -> str:
    buf = Buffer()
    buf.add('# Generated by the Protocol Buffers compiler. DO NOT EDIT!')
    buf.add('# source: {}', ctx.proto_file)
    buf.add('# plugin: {}', __name__)
    buf.add('from dataclasses import dataclass')
    buf.add('')
    for module_name in ctx.adapter_imports:
        buf.add(f'import {module_name}')
    buf.add('')
    for conf_ctx in ctx.configurations:
        buf.add(f'from {ctx.pb2_module} import {conf_ctx.class_name}')
    buf.add('')
    buf.add('')
    for conf_ctx in ctx.configurations:
        buf.add('@dataclass')
        buf.add(f'class {conf_ctx.wires_out_name}:')
        with buf.indent():
            if conf_ctx.outputs:
                for res_ctx in conf_ctx.outputs:
                    buf.add(f'{res_ctx.field_name}: {res_ctx.resource_path}')
            else:
                buf.add('pass')
        buf.add('')
        buf.add('')
        buf.add('@dataclass')
        buf.add(f'class {conf_ctx.wires_in_name}:')
        with buf.indent():
            buf.add(f'__config__: {conf_ctx.class_name}')
            buf.add(f'__wires_out_type__ = {conf_ctx.wires_out_name}')
            for res_ctx in conf_ctx.inputs:
                buf.add(f'{res_ctx.field_name}: {res_ctx.resource_path}')
    return buf.content()
