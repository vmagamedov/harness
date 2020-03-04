import tempfile
from typing import Optional
from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from harness.runtime import Runner, ValidationError
from harness.wires.base import Wire


@pytest.fixture()
def config_type(message_types, package):
    return message_types[f'{package}.Configuration']


@pytest.fixture()
def empty_type(message_types):
    return message_types['google.protobuf.Empty']


async def awaitable(value):
    return value


def test_empty(config_type):
    """
    message Configuration {}
    """
    @dataclass
    class WiresIn:
        config: config_type

    @dataclass
    class WiresOut:
        pass

    runner = Runner(
        config_type,
        WiresIn,
        WiresOut,
    )

    async def main(wires_in):
        return WiresOut()

    with tempfile.NamedTemporaryFile(suffix='.yaml') as config_yaml:
        assert runner.run(main, ['test', config_yaml.name]) == 0


@pytest.mark.parametrize('config_empty', [True, False])
def test_optional_wire(config_type, empty_type, config_empty):
    """
    import "google/protobuf/empty.proto";

    message Configuration {
        google.protobuf.Empty db = 1;
    }
    """
    class DBWire(Wire):
        _value: empty_type

        def configure(self, value: empty_type):
            assert isinstance(value, empty_type), type(value)
            self._value = value

        def __eq__(self, other):
            return self._value == other._value

    @dataclass
    class WiresIn:
        config: config_type
        db: Optional[DBWire]

    @dataclass
    class WiresOut:
        pass

    runner = Runner(
        config_type,
        WiresIn,
        WiresOut,
    )

    main = Mock()
    main.return_value = awaitable(WiresOut())

    with tempfile.NamedTemporaryFile(suffix='.yaml') as config_yaml:
        if not config_empty:
            config_yaml.write(b'db: {}\n')
            config_yaml.flush()
        assert runner.run(main, ['test', config_yaml.name]) == 0

    if config_empty:
        main.assert_called_once_with(
            WiresIn(config=config_type(), db=None),
        )
    else:
        expected_db = DBWire()
        expected_db.configure(empty_type())
        main.assert_called_once_with(
            WiresIn(config=config_type(db=empty_type()), db=expected_db),
        )


@pytest.mark.parametrize('config_empty', [True, False])
def test_required_wire(config_type, empty_type, config_empty):
    """
    import "google/protobuf/empty.proto";

    message Configuration {
        google.protobuf.Empty db = 1 [(validate.rules).message.required = true];
    }
    """
    class DBWire(Wire):
        _value: empty_type

        def configure(self, value: empty_type):
            assert isinstance(value, empty_type), type(value)
            self._value = value

        def __eq__(self, other):
            return self._value == other._value

    @dataclass
    class WiresIn:
        config: config_type
        db: DBWire

    @dataclass
    class WiresOut:
        pass

    runner = Runner(
        config_type,
        WiresIn,
        WiresOut,
    )

    main = Mock()
    with tempfile.NamedTemporaryFile(suffix='.yaml') as config_yaml:
        if config_empty:
            with pytest.raises(ValidationError, match='db is required'):
                runner.run(main, ['test', config_yaml.name])
        else:
            main.return_value = awaitable(WiresOut())
            config_yaml.write(b'db: {}\n')
            config_yaml.flush()
            assert runner.run(main, ['test', config_yaml.name]) == 0
            expected_db = DBWire()
            expected_db.configure(empty_type())
            main.assert_called_once_with(
                WiresIn(config=config_type(db=empty_type()), db=expected_db),
            )
