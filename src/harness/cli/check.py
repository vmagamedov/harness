import sys
from io import StringIO
from typing import List, Optional
from contextlib import closing

from google.protobuf.json_format import ParseDict, ParseError
from google.protobuf.message_factory import GetMessages

from ..runtime._utils import load_config
from ..runtime._validate import validate, ValidationError

from .utils import get_configuration, load_descriptor_set


def check(
    proto: str,
    config: StringIO,
    proto_path: List[str],
    *,
    merge: Optional[StringIO] = None,
    patch: Optional[StringIO] = None,
) -> None:
    with closing(config):
        config_content = config.read()

    if merge is not None:
        with closing(merge):
            merge_content = merge.read()
    else:
        merge_content = None

    if patch is not None:
        with closing(patch):
            patch_content = patch.read()
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
    message_classes = GetMessages(descriptor_set.file)
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
