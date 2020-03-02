import tempfile
from dataclasses import dataclass

import pytest

from harness.runtime import Runner


@pytest.fixture()
def config_type(message_types, package):
    return message_types[f'{package}.Configuration']


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
