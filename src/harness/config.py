from typing import List, Optional
from dataclasses import dataclass

from google.protobuf.descriptor_pb2 import DescriptorProto, FieldDescriptorProto

from validate.validate_pb2 import FieldRules

from .runtime import validate
from .wire_pb2 import HarnessWire, HarnessService


@dataclass
class WireSpec:
    name: str
    type: str
    value: HarnessWire
    optional: bool


@dataclass
class ConfigSpec:
    service: HarnessService
    wires: List[WireSpec]


def translate_descriptor_proto(config_descriptor_proto) -> ConfigSpec:
    for _, option in config_descriptor_proto.options.ListFields():
        if isinstance(option, HarnessService):
            service = option
            break
    else:
        service = HarnessService()
    validate(service)

    wires = []
    for field in config_descriptor_proto.field:
        wire_option = next(
            (option for _, option in field.options.ListFields()
             if isinstance(option, HarnessWire)),
            None,
        )
        if wire_option:
            assert field.type == FieldDescriptorProto.TYPE_MESSAGE, field.type
            validate(wire_option)
            type_ = field.type_name[1:]
            rules_option = next(
                (option for _, option in field.options.ListFields()
                 if isinstance(option, FieldRules)),
                None,
            )
            optional = not (rules_option and rules_option.message.required)
            wires.append(WireSpec(field.name, type_, wire_option, optional))
    return ConfigSpec(service=service, wires=wires)


def translate_descriptor(config_descriptor) -> ConfigSpec:
    proto = DescriptorProto()
    config_descriptor.CopyToProto(proto)
    return translate_descriptor_proto(proto)
