import tempfile

import pytest
from google.protobuf.message_factory import GetMessages

from harness.cli.utils import load_descriptor_set

_counter = 1


@pytest.fixture()
def package():
    global _counter
    try:
        return f'test_{_counter}'
    finally:
        _counter += 1


def _load(package, content):
    src = (
            'syntax = "proto3"; '
            + f'package {package}; '
            + 'import "validate/validate.proto"; '
            + 'import "google/protobuf/timestamp.proto"; '
            + 'import "google/protobuf/duration.proto"; '
            + 'import "google/protobuf/any.proto"; '
            + content
    )
    with tempfile.NamedTemporaryFile(suffix='.proto') as proto_file:
        proto_file.write(src.encode('utf-8'))
        proto_file.flush()
        return load_descriptor_set(proto_file.name)


@pytest.fixture()
def message_proto(request, package):
    return _load(package, request.function.__doc__)


@pytest.fixture()
def message_types(request, package):
    file_descriptor_set = _load(package, request.function.__doc__)
    return GetMessages(file_descriptor_set.file)
