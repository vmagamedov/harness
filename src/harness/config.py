from typing import List, Optional
from dataclasses import dataclass

from google.protobuf.descriptor_pb2 import DescriptorProto, FieldDescriptorProto

from .runtime import validate
from .wire_pb2 import HarnessWire, HarnessService


@dataclass
class WireSpec:
    name: str
    type: Optional[str]
    value: HarnessWire


@dataclass
class ConfigSpec:
    service: HarnessService
    wires: List[WireSpec]


def translate_descriptor_proto(config_descriptor_proto):
    for _, option in config_descriptor_proto.options.ListFields():
        if isinstance(option, HarnessService):
            service = option
            break
    else:
        service = HarnessService()
    validate(service)

    wires = []
    for field in config_descriptor_proto.field:
        for _, option in field.options.ListFields():
            if isinstance(option, HarnessWire):
                validate(option)
                if field.type == FieldDescriptorProto.TYPE_MESSAGE:
                    type_ = field.type_name[1:]
                else:
                    type_ = None
                wires.append(WireSpec(field.name, type_, option))
                break

    return ConfigSpec(service=service, wires=wires)


def translate_descriptor(config_descriptor):
    proto = DescriptorProto()
    config_descriptor.CopyToProto(proto)
    return translate_descriptor_proto(proto)
