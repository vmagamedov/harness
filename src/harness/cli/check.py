import sys
from argparse import FileType
from contextlib import closing

from google.protobuf.json_format import ParseDict, ParseError
from google.protobuf.message_factory import GetMessages

from ..runtime._utils import load_config
from ..runtime._validate import validate, ValidationError

from .utils import get_configuration, load_descriptor_set


def check(args):
    with closing(args.config):
        config_content = args.config.read()

    if args.merge:
        with closing(args.merge):
            merge_content = args.merge.read()
    else:
        merge_content = None

    if args.patch:
        with closing(args.patch):
            patch_content = args.patch.read()
    else:
        patch_content = None

    descriptor_set = load_descriptor_set(args.proto, args.proto_path)
    file_descriptor, = (f for f in descriptor_set.file
                        if args.proto.endswith(f.name))

    config_descriptor = get_configuration(file_descriptor)
    if config_descriptor is None:
        raise Exception(f'Configuration message not found in the {args.proto}')

    config_data = load_config(
        config_content=config_content,
        merge_content=merge_content,
        patch_content=patch_content,
    )
    message_classes = GetMessages(descriptor_set.file)
    config_full_name = '.'.join(filter(None, (
        file_descriptor.package,
        config_descriptor.name,
    )))
    config_cls = message_classes[config_full_name]
    config = config_cls()
    try:
        ParseDict(config_data, config)
    except ParseError as err:
        print(f'Parse error: {err}')
        sys.exit(1)
    try:
        validate(config)
    except ValidationError as err:
        print(f'Validation error: {err}')
        sys.exit(1)


def add_commands(subparsers):
    check_parser = subparsers.add_parser('check')
    check_parser.add_argument('-I', '--proto-path', action='append')
    check_parser.add_argument('proto')
    check_parser.add_argument('config', type=FileType(encoding='utf-8'))
    check_parser.add_argument('--merge', type=FileType(encoding='utf-8'),
                              default=None)
    check_parser.add_argument('--patch', type=FileType(encoding='utf-8'),
                              default=None)
    check_parser.set_defaults(func=check)
