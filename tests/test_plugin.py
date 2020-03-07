from textwrap import dedent

import pytest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest

from harness.plugin.main import process, ConfigurationError


@pytest.fixture()
def proto_file_name(package, message_proto):
    return next(f.name for f in message_proto.file if f.package == package)


@pytest.fixture()
def python_request(proto_file_name, message_proto):
    return CodeGeneratorRequest(
        parameter='runtime=python',
        file_to_generate=[proto_file_name],
        proto_file=message_proto.file,
    )


def prepare(content):
    return dedent(content).strip()


def test_invalid_request():
    with pytest.raises(
        ConfigurationError, match='Runtime parameter is not specified',
    ):
        process(CodeGeneratorRequest())

    with pytest.raises(
        ConfigurationError, match='Unknown runtime',
    ):
        process(CodeGeneratorRequest(parameter='runtime=invalid'))

    with pytest.raises(
        ConfigurationError, match='Missing configuration message',
    ):
        process(CodeGeneratorRequest(
            parameter='runtime=python',
            file_to_generate=['svc.proto'],
            proto_file=[dict(name='svc.proto')],
        ))


def test_python_optional_input(python_request):
    """
    import "google/protobuf/wrappers.proto";
    import "harness/wire.proto";

    message Configuration {
        google.protobuf.StringValue db = 1 [
            (harness.wire).input.type = "path.to.implementation.Wire"
        ];
    }
    """
    response = process(python_request)
    assert response.file[0].name.endswith('_wires.py')

    expected = prepare(f"""
    from typing import Optional
    from dataclasses import dataclass

    import path.to.implementation


    @dataclass
    class WiresIn:
        db: Optional[path.to.implementation.Wire]


    @dataclass
    class WiresOut:
        pass
    """)
    assert expected in response.file[0].content


def test_python_required_input(python_request):
    """
    import "google/protobuf/wrappers.proto";
    import "harness/wire.proto";

    message Configuration {
        google.protobuf.StringValue db = 1 [
            (validate.rules).message.required = true,
            (harness.wire).input.type = "path.to.implementation.Wire"
        ];
    }
    """
    response = process(python_request)
    assert response.file[0].name.endswith('_wires.py')

    expected = prepare(f"""
    from dataclasses import dataclass

    import path.to.implementation


    @dataclass
    class WiresIn:
        db: path.to.implementation.Wire


    @dataclass
    class WiresOut:
        pass
    """)
    assert expected in response.file[0].content
