from ipaddress import ip_address

import pytest

from harness.runtime._validate import validate, ValidationError


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


def test_disabled(message_type):
    """
    message Message {
        message Inner {
            option (validate.disabled) = true;
            string value = 1 [(validate.rules).string.const = "valid"];
        }
        Inner field = 1;
    }
    """
    validate(message_type(field=dict(value="invalid")))


def test_oneof_required(message_type):
    """
    message Message {
        oneof type {
            option (validate.required) = true;
            string foo = 1;
            int32 bar = 2;
        }
    }
    """
    validate(message_type(foo="test"))
    validate(message_type(bar=42))
    with pytest.raises(ValidationError, match='Oneof type is required'):
        validate(message_type())


def test_float_const(message_type):
    """
    message Message {
        float value = 1 [(validate.rules).float.const = 4.2];
    }
    """
    validate(message_type(value=4.2))
    with pytest.raises(ValidationError, match='value not equal to'):
        validate(message_type(value=2.4))


def test_timestamp_lt(message_type, timestamp_type):
    """
    message Message {
        google.protobuf.Timestamp value = 1 [
            (validate.rules).timestamp.lt = {seconds: 1000}
        ];
    }
    """
    validate(message_type(value=timestamp_type(seconds=999)))
    with pytest.raises(ValidationError, match='is not lesser than'):
        validate(message_type(value=timestamp_type(seconds=1000)))


def test_timestamp_within(message_type, timestamp_type):
    """
    message Message {
        google.protobuf.Timestamp value = 1 [
            (validate.rules).timestamp.within = {seconds: 60}
        ];
    }
    """
    value = timestamp_type()
    value.GetCurrentTime()
    validate(message_type(value=value))
    valid_seconds = value.seconds
    with pytest.raises(ValidationError, match='value is not within 60s from now'):
        value.seconds = valid_seconds - 100
        validate(message_type(value=value))
    with pytest.raises(ValidationError, match='value is not within 60s from now'):
        value.seconds = valid_seconds - 100
        validate(message_type(value=value))
    value.seconds = valid_seconds
    validate(message_type(value=value))


def test_duration_in(message_type, duration_type):
    """
    message Message {
        google.protobuf.Duration value = 1 [
            (validate.rules).duration.in = {seconds: 60},
            (validate.rules).duration.in = {seconds: 30}
        ];
    }
    """
    validate(message_type(value=duration_type(seconds=60)))
    with pytest.raises(ValidationError, match='value not in {60s, 30s}'):
        validate(message_type(value=duration_type(seconds=120)))


def test_duration_lte(message_type, duration_type):
    """
    message Message {
        google.protobuf.Duration value = 1 [
            (validate.rules).duration.lte = {seconds: 60}
        ];
    }
    """
    validate(message_type(value=duration_type(seconds=60)))
    with pytest.raises(ValidationError, match='value is not lesser than or equal to 60s'):
        validate(message_type(value=duration_type(seconds=60, nanos=1)))


def test_enum_defined_only(message_type):
    """
    message Message {
        enum Foo {
            A = 0;
            B = 1;
        }
        Foo value = 1 [(validate.rules).enum.defined_only = true];
    }
    """
    validate(message_type())
    validate(message_type(value=1))
    with pytest.raises(ValidationError, match='value is not defined'):
        validate(message_type(value=2))


def test_repeated_unique(message_type):
    """
    message Message {
        repeated int32 value = 1 [(validate.rules).repeated.unique = true];
    }
    """
    validate(message_type(value=[1, 2, 3]))
    with pytest.raises(ValidationError, match='value must contain unique items; repeated items: \\[2, 3\\]'):
        validate(message_type(value=[1, 2, 3, 2, 4, 3, 5]))


def test_repeated_items(message_type):
    """
    message Message {
        repeated int32 field = 1 [(validate.rules).repeated.items.int32.lt = 5];
    }
    """
    validate(message_type(field=[1, 2, 3, 4]))
    with pytest.raises(ValidationError, match='field\\[\\] is not lesser than 5'):
        validate(message_type(field=[1, 2, 3, 4, 5]))


def test_map_key(message_type):
    """
    message Message {
        map<string, int32> field = 1 [(validate.rules).map.keys.string.min_len = 3];
    }
    """
    validate(message_type(field={'test': 42}))
    with pytest.raises(ValidationError, match='field<key> length is less than 3'):
        validate(message_type(field={'t': 42}))


def test_map_values(message_type):
    """
    message Message {
        map<string, int32> field = 1 [(validate.rules).map.values.int32.const = 42];
    }
    """
    validate(message_type(field={'test': 42}))
    with pytest.raises(ValidationError, match='field<value> not equal to 42'):
        validate(message_type(field={'test': 43}))


def test_any_in(message_type, any_type, duration_type, timestamp_type):
    """
    message Message {
        google.protobuf.Any field = 1 [(validate.rules).any.in = "type.googleapis.com/google.protobuf.Duration"];
    }
    """
    any_1 = any_type()
    any_1.Pack(duration_type(seconds=42))
    validate(message_type(field=any_1))
    with pytest.raises(ValidationError, match='field.type_url not in'):
        any_2 = any_type()
        any_2.Pack(timestamp_type(seconds=42))
        validate(message_type(field=any_2))


def test_nested(message_type):
    """
    message Message {
        message Inner {
            string value = 1 [(validate.rules).string.const = "valid"];
        }
        Inner field = 1;
    }
    """
    validate(message_type())
    validate(message_type(field=dict(value="valid")))
    with pytest.raises(ValidationError, match="value not equal to 'valid'"):
        validate(message_type(field=dict(value="invalid")))


def test_message_skip(message_type):
    """
    message Message {
        message Inner {
            string value = 1 [(validate.rules).string.const = "valid"];
        }
        Inner field = 1 [(validate.rules).message.skip = true];
    }
    """
    validate(message_type(field=dict(value="invalid")))


def test_message_required(message_type):
    """
    message Message {
        message Inner {
            string value = 1;
        }
        Inner field = 1 [(validate.rules).message.required = true];
    }
    """
    validate(message_type(field=dict()))
    validate(message_type(field=dict(value='test')))
    with pytest.raises(ValidationError, match="field is required"):
        validate(message_type())


def test_email(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.email = true];
    }
    """
    validate(message_type(field="admin@example.com"))
    validate(message_type(field="Jean-Luc Picard <jean-luc.pickard@starfleet.milkyway>"))
    with pytest.raises(ValidationError, match='field contains invalid email address'):
        validate(message_type(field="example.com"))
    with pytest.raises(ValidationError, match='field contains more than one email address'):
        validate(message_type(field="foo@example.com, bar@example.com"))


def test_hostname(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.hostname = true];
    }
    """
    validate(message_type(field="example.com"))
    validate(message_type(field="Example.com"))
    with pytest.raises(ValidationError, match='field contains invalid hostname'):
        validate(message_type(field="-example.com"))


def test_string_ip(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.ip = true];
    }
    """
    validate(message_type(field="0.0.0.0"))
    validate(message_type(field="127.0.0.1"))
    validate(message_type(field="::1"))
    validate(message_type(field="2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
    with pytest.raises(ValidationError, match='field contains invalid IP address'):
        validate(message_type(field="0.0.0"))


def test_string_ipv4(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.ipv4 = true];
    }
    """
    validate(message_type(field="0.0.0.0"))
    validate(message_type(field="127.0.0.1"))
    with pytest.raises(ValidationError, match='field contains invalid IPv4 address'):
        validate(message_type(field="0.0.0"))
    with pytest.raises(ValidationError, match='field contains invalid IPv4 address'):
        validate(message_type(field="2001:0db8:85a3:0000:0000:8a2e:0370:7334"))


def test_string_ipv6(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.ipv6 = true];
    }
    """
    validate(message_type(field="::1"))
    validate(message_type(field="2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
    with pytest.raises(ValidationError, match='field contains invalid IPv6 address'):
        validate(message_type(field="2001:0db8:85a3:0000:0000:8a2e:0370:733."))
    with pytest.raises(ValidationError, match='field contains invalid IPv6 address'):
        validate(message_type(field="127.0.0.1"))


def test_bytes_ip(message_type):
    """
    message Message {
        bytes field = 1 [(validate.rules).bytes.ip = true];
    }
    """
    validate(message_type(field=ip_address("0.0.0.0").packed))
    validate(message_type(field=ip_address("127.0.0.1").packed))
    validate(message_type(field=ip_address("::1").packed))
    validate(message_type(field=ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334").packed))
    with pytest.raises(ValidationError, match='field contains invalid IP address'):
        validate(message_type(field=ip_address("0.0.0.0").packed[:-1]))


def test_bytes_ipv4(message_type):
    """
    message Message {
        bytes field = 1 [(validate.rules).bytes.ipv4 = true];
    }
    """
    validate(message_type(field=ip_address("0.0.0.0").packed))
    validate(message_type(field=ip_address("127.0.0.1").packed))
    with pytest.raises(ValidationError, match='field contains invalid IPv4 address'):
        validate(message_type(field=b'deadbeef'))
    with pytest.raises(ValidationError, match='field contains invalid IPv4 address'):
        validate(message_type(field=ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334").packed))


def test_bytes_ipv6(message_type):
    """
    message Message {
        bytes field = 1 [(validate.rules).bytes.ipv6 = true];
    }
    """
    validate(message_type(field=ip_address("::1").packed))
    validate(message_type(field=ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334").packed))
    with pytest.raises(ValidationError, match='field contains invalid IPv6 address'):
        validate(message_type(field=b'deadbeef'))
    with pytest.raises(ValidationError, match='field contains invalid IPv6 address'):
        validate(message_type(field=ip_address("127.0.0.1").packed))


def test_address(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.address = true];
    }
    """
    validate(message_type(field="::1"))
    validate(message_type(field="127.0.0.1"))
    validate(message_type(field="Example.com"))
    with pytest.raises(ValidationError, match='field contains invalid address'):
        validate(message_type(field="invalid"))


def test_uri(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.uri = true];
    }
    """
    validate(message_type(field="http://google.com"))
    validate(message_type(field="http://127.0.0.1/page.html#fragment"))
    with pytest.raises(ValidationError, match='field contains invalid URI'):
        validate(message_type(field="/local/path"))


def test_uri_ref(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.uri_ref = true];
    }
    """
    validate(message_type(field="http://google.com"))
    validate(message_type(field="/local/path"))
    with pytest.raises(ValidationError, match='field contains invalid URI-reference'):
        validate(message_type(field="\\invalid\\path"))


def test_uuid(message_type):
    """
    message Message {
        string field = 1 [(validate.rules).string.uuid = true];
    }
    """
    validate(message_type(field="adbf3fd4-6a41-41a8-b5c1-df09adc3a9b3"))
    validate(message_type(field="ADBF3FD4-6A41-41A8-B5C1-DF09ADC3A9B3"))
    with pytest.raises(ValidationError, match='field contains invalid UUID'):
        validate(message_type(field="adbf3fd46a4141a8b5c1df09adc3a9b3"))
    with pytest.raises(ValidationError, match='field contains invalid UUID'):
        validate(message_type(field="adbf3fd4-6a41-41a8-b5c1-df09adc3a9b3-ext"))
