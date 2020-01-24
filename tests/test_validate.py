import tempfile

import pytest
from google.protobuf.message_factory import GetMessages

from harness.cli.kube import load
from harness.runtime._validate import validate, ValidationFailed


_counter = 1


def _get_package():
    global _counter
    try:
        return f'test_{_counter}'
    finally:
        _counter += 1


def message_factory(content):
    package = _get_package()
    src = (
        'syntax = "proto3"; '
        + f'package {package}; '
        + 'import "validate/validate.proto"; '
        + f'message Message {{ {content} }}'
    )
    with tempfile.NamedTemporaryFile(suffix='.proto') as proto_file:
        proto_file.write(src.encode('utf-8'))
        proto_file.flush()
        file_descriptor_set = load(proto_file.name)
    return GetMessages(file_descriptor_set.file)[f'{package}.Message']


@pytest.fixture()
def message_type(request):
    return message_factory(request.function.__doc__)


def test_float_const(message_type):
    """
    float value = 1 [(validate.rules).float.const = 4.2];
    """
    validate(message_type(value=4.2))
    with pytest.raises(ValidationFailed, match='value not equal to'):
        validate(message_type(value=2.4))
