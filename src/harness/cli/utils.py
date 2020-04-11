import tempfile
from typing import Optional, List, Sequence, Dict, Type, cast
from pathlib import Path

import pkg_resources
from grpc_tools import protoc
from google.protobuf.message import Message
from google.protobuf.descriptor_pb2 import FileDescriptorSet, FileDescriptorProto
from google.protobuf.descriptor_pb2 import DescriptorProto
from google.protobuf.message_factory import GetMessages


def get_messages(files: Sequence[FileDescriptorProto]) -> Dict[str, Type[Message]]:
    mapping = GetMessages(files)  # type: ignore
    return cast("Dict[str, Type[Message]]", mapping)


def load_descriptor_set(
    proto_file: str, proto_path: Optional[List[str]] = None
) -> FileDescriptorSet:
    wkt_protos = pkg_resources.resource_filename("grpc_tools", "_proto")
    validate_protos = str(
        Path(
            pkg_resources.resource_filename("validate", "validate.proto")
        ).parent.parent
    )
    harness_protos = str(Path(__file__).parent.parent.parent.absolute())
    with tempfile.NamedTemporaryFile() as f:
        args = [
            "grpc_tools.protoc",
            "--include_imports",
            f"--proto_path={wkt_protos}",
            f"--proto_path={validate_protos}",
            f"--proto_path={harness_protos}",
            f"--proto_path={Path(proto_file).parent}",
            f"--descriptor_set_out={f.name}",
        ]
        if proto_path:
            args.extend(f"--proto_path={p}" for p in proto_path)
        args.append(proto_file)
        result = protoc.main(args)
        if result != 0:
            raise Exception("Failed to call protoc")
        content = f.read()
    return FileDescriptorSet.FromString(content)


def get_configuration(
    file_descriptor: FileDescriptorProto,
) -> Optional[DescriptorProto]:
    for message_type in file_descriptor.message_type:
        if message_type.name == "Configuration":
            return message_type
    return None
