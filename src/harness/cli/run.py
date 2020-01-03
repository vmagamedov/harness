import asyncio
import inspect
import argparse
import importlib
from typing import Any, Type, Callable
from contextlib import AsyncExitStack
from dataclasses import fields, dataclass

import yaml
from jsonpatch import JsonPatch
from grpclib.utils import graceful_exit
from json_merge_patch import merge
from google.protobuf.message import Message
from google.protobuf.json_format import ParseDict


async def wrapper(service_func, wires_in_type, wires_out_type, config):
    async with AsyncExitStack() as stack:
        input_wires = {}
        for field in fields(wires_in_type):
            if field.name == '__config__':
                continue
            wire_config = getattr(config, field.name)
            wire = field.type()
            wire.configure(wire_config)
            await stack.enter_async_context(wire)
            input_wires[field.name] = wire
        wires_in = wires_in_type(**input_wires, __config__=config)

        wires_out = await service_func(wires_in)
        if not isinstance(wires_out, wires_out_type):
            raise RuntimeError(
                f'{service_func} returned invalid type: {type(wires_out)!r}; '
                f'expected: {wires_out_type!r}'
            )

        waiters = set()
        output_wires = []
        for field in fields(wires_out_type):
            wire = getattr(wires_out, field.name)
            wire_config = getattr(config, field.name)
            wire.configure(wire_config)
            await stack.enter_async_context(wire)
            waiters.add(wire.wait_closed())
            output_wires.append(wire)
        with graceful_exit(output_wires):
            await asyncio.wait(waiters, return_when=asyncio.FIRST_COMPLETED)


@dataclass
class Spec:
    func: Callable[[Any], Any]
    config_type: Type[Message]
    wires_in_type: type
    wires_out_type: type


def load_spec(path: str) -> Spec:
    module_name, _, name = path.partition(':')
    if not name:
        name = 'main'

    module = importlib.import_module(module_name)
    service_func = getattr(module, name)
    signature = inspect.getfullargspec(service_func)
    if len(signature.args) - len(signature.defaults or ()) != 1:
        raise SystemExit(f'"{module_name}:{name}" function must have exactly '
                         f'one positional argument')

    arg_name = signature.args[0]
    if arg_name not in signature.annotations:
        raise SystemExit(f'"{module_name}:{name}" function has missing type '
                         f'annotation for the "{arg_name}" argument')

    wires_in_type = signature.annotations[arg_name]
    wires_in_annotations = getattr(wires_in_type, '__annotations__', {})
    if '__config__' not in wires_in_annotations:
        raise SystemExit(f'"{module_name}:{name}" function has invalid '
                         f'annotation for the "{arg_name}" argument')

    wires_out_type = wires_in_type.__wires_out_type__
    return_annotation = signature.annotations.get('return')
    if not return_annotation:
        raise SystemExit(f'"{module_name}:{name}" function '
                         f'is missing return annotation')
    elif return_annotation is not wires_out_type:
        raise SystemExit(f'"{module_name}:{name}" function '
                         f'has invalid return annotation')
    return Spec(
        func=service_func,
        config_type=wires_in_annotations['__config__'],
        wires_in_type=wires_in_type,
        wires_out_type=wires_out_type,
    )


def run(args):
    spec = load_spec(args.path)

    with args.config:
        config_data = yaml.safe_load(args.config)
    if config_data is None:
        config_data = {}
    if not isinstance(config_data, dict):
        raise SystemExit(f'Invalid configuration: {args.config!r}')

    if args.merge is not None:
        with args.merge:
            merge_data = yaml.safe_load(args.merge)
        config_data = merge(config_data, merge_data)

    if args.patch is not None:
        with args.patch:
            patch_data = yaml.safe_load(args.patch)
        json_patch = JsonPatch(patch_data)
        config_data = json_patch.apply(config_data)

    config = spec.config_type()
    ParseDict(config_data, config)
    asyncio.run(wrapper(
        spec.func,
        spec.wires_in_type,
        spec.wires_out_type,
        config,
    ))


def add_commands(subparsers):
    parser = subparsers.add_parser('run')
    parser.add_argument(
        'path',
        help='Import path to the service function; '
             'path.to.svc or path.to.svc:main',
    )
    parser.add_argument(
        'config',
        type=argparse.FileType('r', encoding='utf-8'),
        help='Configuration file in the YAML format',
    )
    parser.add_argument(
        '--merge',
        default=None,
        type=argparse.FileType('r', encoding='utf-8'),
        help='Merge config with a file',
    )
    parser.add_argument(
        '--patch',
        default=None,
        type=argparse.FileType('r', encoding='utf-8'),
        help='Patch config with a file',
    )
    parser.set_defaults(func=run)
