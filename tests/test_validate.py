import tempfile

import pytest
from google.protobuf import any_pb2
from google.protobuf import struct_pb2
from google.protobuf.message_factory import GetMessages

from harness.cli.kube import load
from harness.runtime._validate import validate, ValidationFailed


_counter = 1


@pytest.fixture()
def package():
    global _counter
    try:
        return f'test_{_counter}'
    finally:
        _counter += 1


def message_factory(package, content):
    src = (
        'syntax = "proto3"; '
        + f'package {package}; '
        + 'import "validate/validate.proto"; '
        + 'import "google/protobuf/timestamp.proto"; '
        + 'import "google/protobuf/duration.proto"; '
        + 'import "google/protobuf/any.proto"; '
        + f'message Message {{ {content} }}'
    )
    with tempfile.NamedTemporaryFile(suffix='.proto') as proto_file:
        proto_file.write(src.encode('utf-8'))
        proto_file.flush()
        file_descriptor_set = load(proto_file.name)
    return GetMessages(file_descriptor_set.file)


@pytest.fixture()
def message_types(request, package):
    return message_factory(package, request.function.__doc__)


@pytest.fixture()
def message_type(message_types, package):
    return message_types[f'{package}.Message']


@pytest.fixture()
def timestamp_type(message_types):
    return message_types['google.protobuf.Timestamp']


@pytest.fixture()
def duration_type(message_types):
    return message_types['google.protobuf.Duration']


@pytest.fixture()
def any_type(message_types):
    return message_types['google.protobuf.Any']


def test_float_const(message_type):
    """
    float value = 1 [(validate.rules).float.const = 4.2];
    """
    validate(message_type(value=4.2))
    with pytest.raises(ValidationFailed, match='value not equal to'):
        validate(message_type(value=2.4))


def test_timestamp_lt(message_type, timestamp_type):
    """
    google.protobuf.Timestamp value = 1 [
        (validate.rules).timestamp.lt = {seconds: 1000}
    ];
    """
    validate(message_type(value=timestamp_type(seconds=999)))
    with pytest.raises(ValidationFailed, match='is not lesser than'):
        validate(message_type(value=timestamp_type(seconds=1000)))


def test_timestamp_within(message_type, timestamp_type):
    """
    google.protobuf.Timestamp value = 1 [
        (validate.rules).timestamp.within = {seconds: 60}
    ];
    """
    value = timestamp_type()
    value.GetCurrentTime()
    validate(message_type(value=value))
    valid_seconds = value.seconds
    with pytest.raises(ValidationFailed, match='value is not within 60s from now'):
        value.seconds = valid_seconds - 100
        validate(message_type(value=value))
    with pytest.raises(ValidationFailed, match='value is not within 60s from now'):
        value.seconds = valid_seconds - 100
        validate(message_type(value=value))
    value.seconds = valid_seconds
    validate(message_type(value=value))


def test_duration_in(message_type, duration_type):
    """
    google.protobuf.Duration value = 1 [
        (validate.rules).duration.in = {seconds: 60},
        (validate.rules).duration.in = {seconds: 30}
    ];
    """
    validate(message_type(value=duration_type(seconds=60)))
    with pytest.raises(ValidationFailed, match='value not in {60s, 30s}'):
        validate(message_type(value=duration_type(seconds=120)))


def test_duration_lte(message_type, duration_type):
    """
    google.protobuf.Duration value = 1 [
        (validate.rules).duration.lte = {seconds: 60}
    ];
    """
    validate(message_type(value=duration_type(seconds=60)))
    with pytest.raises(ValidationFailed, match='value is not lesser than or equal to 60s'):
        validate(message_type(value=duration_type(seconds=60, nanos=1)))


def test_enum_defined_only(message_type):
    """
    enum Foo {
        A = 0;
        B = 1;
    }
    Foo value = 1 [(validate.rules).enum.defined_only = true];
    """
    validate(message_type())
    validate(message_type(value=1))
    with pytest.raises(ValidationFailed, match='value is not defined'):
        validate(message_type(value=2))


def test_repeated_unique(message_type):
    """
    repeated int32 value = 1 [(validate.rules).repeated.unique = true];
    """
    validate(message_type(value=[1, 2, 3]))
    with pytest.raises(ValidationFailed, match='value must contain unique items; repeated items: \\[2, 3\\]'):
        validate(message_type(value=[1, 2, 3, 2, 4, 3, 5]))


def test_repeated_items(message_type):
    """
    repeated int32 field = 1 [(validate.rules).repeated.items.int32.lt = 5];
    """
    validate(message_type(field=[1, 2, 3, 4]))
    with pytest.raises(ValidationFailed, match='field\\[\\] is not lesser than 5'):
        validate(message_type(field=[1, 2, 3, 4, 5]))


def test_map_key(message_type):
    """
    map<string, int32> field = 1 [(validate.rules).map.keys.string.min_len = 3];
    """
    validate(message_type(field={'test': 42}))
    with pytest.raises(ValidationFailed, match='field<key> length is less than 3'):
        validate(message_type(field={'t': 42}))


def test_map_values(message_type):
    """
    map<string, int32> field = 1 [(validate.rules).map.values.int32.const = 42];
    """
    validate(message_type(field={'test': 42}))
    with pytest.raises(ValidationFailed, match='field<value> not equal to 42'):
        validate(message_type(field={'test': 43}))


def test_any_in(message_type, any_type, duration_type, timestamp_type):
    """
    google.protobuf.Any field = 1 [(validate.rules).any.in = "type.googleapis.com/google.protobuf.Duration"];
    """
    any_1 = any_type()
    any_1.Pack(duration_type(seconds=42))
    validate(message_type(field=any_1))
    with pytest.raises(ValidationFailed, match='field.type_url not in'):
        any_2 = any_type()
        any_2.Pack(timestamp_type(seconds=42))
        validate(message_type(field=any_2))
