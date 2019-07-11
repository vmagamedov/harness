import codecs
import asyncio
import inspect
import argparse
import importlib

import yaml
from google.protobuf.json_format import ParseDict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('location')
    parser.add_argument('config')
    args = parser.parse_args()

    module_name, _, name = args.location.partition(':')
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

    config_type = wires_in_annotations['__config__']
    with codecs.open(args.config, 'rb', 'utf-8') as f:
        config_data = yaml.safe_load(f)
        if config_data is None:
            config_data = {}
        if not isinstance(config_data, dict):
            raise SystemExit(f'Invalid configuration: {args.config!r}')

    config = config_type()
    ParseDict(config_data, config)

    wrapper = wires_in_type.__wrapper__()
    asyncio.run(wrapper(service_func, config))
