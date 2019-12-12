import codecs
import asyncio
import inspect
import argparse
import importlib
from contextlib import AsyncExitStack
from dataclasses import fields

import yaml
from grpclib.utils import graceful_exit
from google.protobuf.json_format import ParseDict


async def wrapper(service_func, wires_in_type, wires_out_type, config):
    async with AsyncExitStack() as stack:
        input_resources = {}
        for field in fields(wires_in_type):
            if field.name == '__config__':
                continue
            resource_config = getattr(config, field.name)
            resource = field.type()
            resource.configure(resource_config)
            await stack.enter_async_context(resource)
            input_resources[field.name] = resource
        wires_in = wires_in_type(**input_resources, __config__=config)

        wires_out = await service_func(wires_in)
        if not isinstance(wires_out, wires_out_type):
            raise RuntimeError(
                f'{service_func} returned invalid type: {type(wires_out)!r}; '
                f'expected: {wires_out_type!r}'
            )

        waiters = set()
        output_resources = []
        for field in fields(wires_out_type):
            resource = getattr(wires_out, field.name)
            resource_config = getattr(config, field.name)
            resource.configure(resource_config)
            await stack.enter_async_context(resource)
            waiters.add(resource.wait_closed())
            output_resources.append(resource)
        with graceful_exit(output_resources):
            await asyncio.wait(waiters, return_when=asyncio.FIRST_COMPLETED)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        help='Import path to the service function; '
             'path.to.svc or path.to.svc:main',
    )
    parser.add_argument(
        'config',
        help='Configuration file in the YAML format',
    )
    args = parser.parse_args()

    module_name, _, name = args.path.partition(':')
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

    config_type = wires_in_annotations['__config__']
    with codecs.open(args.config, 'rb', 'utf-8') as f:
        config_data = yaml.safe_load(f)
        if config_data is None:
            config_data = {}
        if not isinstance(config_data, dict):
            raise SystemExit(f'Invalid configuration: {args.config!r}')

    config = config_type()
    ParseDict(config_data, config)
    asyncio.run(wrapper(service_func, wires_in_type, wires_out_type, config))
