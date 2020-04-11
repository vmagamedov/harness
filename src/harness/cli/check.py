import sys
from io import StringIO
from typing import List, Optional
from contextlib import closing

from google.protobuf.json_format import ParseDict, ParseError

from ..runtime._utils import load_config
from ..runtime._validate import validate, ValidationError

from .utils import get_configuration, load_descriptor_set, get_messages


def check(
    proto: str,
    config_file: StringIO,
    proto_path: List[str],
    *,
    merge_file: Optional[StringIO] = None,
    patch_file: Optional[StringIO] = None,
) -> None:
    with closing(config_file):
        config_content = config_file.read()

    merge_content: Optional[str]
    if merge_file is not None:
        with closing(merge_file):
            merge_content = merge_file.read()
    else:
        merge_content = None

    patch_content: Optional[str]
    if patch_file is not None:
        with closing(patch_file):
            patch_content = patch_file.read()
    else:
        patch_content = None

    descriptor_set = load_descriptor_set(proto, proto_path)
    (file_descriptor,) = (f for f in descriptor_set.file if proto.endswith(f.name))

    config_descriptor = get_configuration(file_descriptor)
    if config_descriptor is None:
        raise Exception(f"Configuration message not found in the {proto}")

    config_data = load_config(
        config_content=config_content,
        merge_content=merge_content,
        patch_content=patch_content,
    )
    message_classes = get_messages(descriptor_set.file)
    config_full_name = ".".join(
        filter(None, (file_descriptor.package, config_descriptor.name))
    )
    config_cls = message_classes[config_full_name]
    config = config_cls()
    try:
        ParseDict(config_data, config)
    except ParseError as err:
        print(f"Parse error: {err}")
        sys.exit(1)
    try:
        validate(config)
    except ValidationError as err:
        print(f"Validation error: {err}")
        sys.exit(1)
    print("OK")
