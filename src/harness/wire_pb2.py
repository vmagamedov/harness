# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: harness/wire.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2
from validate import validate_pb2 as validate_dot_validate__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='harness/wire.proto',
  package='harness',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=b'\n\x12harness/wire.proto\x12\x07harness\x1a google/protobuf/descriptor.proto\x1a\x17validate/validate.proto\"Y\n\x04Mark\x12(\n\x08protocol\x18\x01 \x01(\x0e\x32\x16.harness.Mark.Protocol\"\'\n\x08Protocol\x12\x07\n\x03TCP\x10\x00\x12\x08\n\x04HTTP\x10\x01\x12\x08\n\x04GRPC\x10\x02\"\x85\x01\n\x05Input\x12\x15\n\x04type\x18\x01 \x02(\tB\x07\xfa\x42\x04r\x02\x10\x01\x12#\n\x05reach\x18\x02 \x01(\x0e\x32\x14.harness.Input.Reach\"@\n\x05Reach\x12\r\n\tLOCALHOST\x10\x00\x12\r\n\tNAMESPACE\x10\x01\x12\x0b\n\x07\x43LUSTER\x10\x02\x12\x0c\n\x08\x45XTERNAL\x10\x03\"\x86\x01\n\x06Output\x12\x15\n\x04type\x18\x01 \x02(\tB\x07\xfa\x42\x04r\x02\x10\x01\x12&\n\x06\x65xpose\x18\x02 \x01(\x0e\x32\x16.harness.Output.Expose\"=\n\x06\x45xpose\x12\x0b\n\x07PRIVATE\x10\x00\x12\x0c\n\x08HEADLESS\x10\x01\x12\x0c\n\x08INTERNAL\x10\x02\x12\n\n\x06PUBLIC\x10\x03\"W\n\x04Wire\x12\x1f\n\x05input\x18\x01 \x01(\x0b\x32\x0e.harness.InputH\x00\x12!\n\x06output\x18\x02 \x01(\x0b\x32\x0f.harness.OutputH\x00\x42\x0b\n\x04type\x12\x03\xf8\x42\x01\"\xa8\x02\n\x07Service\x12\x0c\n\x04name\x18\x01 \x01(\t\x12-\n\tcontainer\x18\x02 \x01(\x0b\x32\x1a.harness.Service.Container\x1a\'\n\x08Resource\x12\x0b\n\x03\x63pu\x18\x01 \x01(\t\x12\x0e\n\x06memory\x18\x02 \x01(\t\x1a\x63\n\tResources\x12+\n\x08requests\x18\x01 \x01(\x0b\x32\x19.harness.Service.Resource\x12)\n\x06limits\x18\x02 \x01(\x0b\x32\x19.harness.Service.Resource\x1aR\n\tContainer\x12\x12\n\nrepository\x18\x01 \x01(\t\x12\x31\n\tresources\x18\x02 \x01(\x0b\x32\x1a.harness.Service.ResourcesB\x02\x18\x01:;\n\x04wire\x12\x1d.google.protobuf.FieldOptions\x18\xd1\x0f \x01(\x0b\x32\r.harness.Wire:;\n\x04mark\x12\x1d.google.protobuf.FieldOptions\x18\xd2\x0f \x01(\x0b\x32\r.harness.Mark:C\n\x07service\x12\x1f.google.protobuf.MessageOptions\x18\xd1\x0f \x01(\x0b\x32\x10.harness.Service'
  ,
  dependencies=[google_dot_protobuf_dot_descriptor__pb2.DESCRIPTOR,validate_dot_validate__pb2.DESCRIPTOR,])


WIRE_FIELD_NUMBER = 2001
wire = _descriptor.FieldDescriptor(
  name='wire', full_name='harness.wire', index=0,
  number=2001, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
MARK_FIELD_NUMBER = 2002
mark = _descriptor.FieldDescriptor(
  name='mark', full_name='harness.mark', index=1,
  number=2002, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
SERVICE_FIELD_NUMBER = 2001
service = _descriptor.FieldDescriptor(
  name='service', full_name='harness.service', index=2,
  number=2001, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)

_MARK_PROTOCOL = _descriptor.EnumDescriptor(
  name='Protocol',
  full_name='harness.Mark.Protocol',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='TCP', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HTTP', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GRPC', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=140,
  serialized_end=179,
)
_sym_db.RegisterEnumDescriptor(_MARK_PROTOCOL)

_INPUT_REACH = _descriptor.EnumDescriptor(
  name='Reach',
  full_name='harness.Input.Reach',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='LOCALHOST', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NAMESPACE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CLUSTER', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXTERNAL', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=251,
  serialized_end=315,
)
_sym_db.RegisterEnumDescriptor(_INPUT_REACH)

_OUTPUT_EXPOSE = _descriptor.EnumDescriptor(
  name='Expose',
  full_name='harness.Output.Expose',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PRIVATE', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HEADLESS', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INTERNAL', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PUBLIC', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=391,
  serialized_end=452,
)
_sym_db.RegisterEnumDescriptor(_OUTPUT_EXPOSE)


_MARK = _descriptor.Descriptor(
  name='Mark',
  full_name='harness.Mark',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='protocol', full_name='harness.Mark.protocol', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _MARK_PROTOCOL,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=90,
  serialized_end=179,
)


_INPUT = _descriptor.Descriptor(
  name='Input',
  full_name='harness.Input',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='harness.Input.type', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\004r\002\020\001', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='reach', full_name='harness.Input.reach', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _INPUT_REACH,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=182,
  serialized_end=315,
)


_OUTPUT = _descriptor.Descriptor(
  name='Output',
  full_name='harness.Output',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='harness.Output.type', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\004r\002\020\001', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='expose', full_name='harness.Output.expose', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _OUTPUT_EXPOSE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=318,
  serialized_end=452,
)


_WIRE = _descriptor.Descriptor(
  name='Wire',
  full_name='harness.Wire',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='input', full_name='harness.Wire.input', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='output', full_name='harness.Wire.output', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='type', full_name='harness.Wire.type',
      index=0, containing_type=None, fields=[], serialized_options=b'\370B\001'),
  ],
  serialized_start=454,
  serialized_end=541,
)


_SERVICE_RESOURCE = _descriptor.Descriptor(
  name='Resource',
  full_name='harness.Service.Resource',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cpu', full_name='harness.Service.Resource.cpu', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='memory', full_name='harness.Service.Resource.memory', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=616,
  serialized_end=655,
)

_SERVICE_RESOURCES = _descriptor.Descriptor(
  name='Resources',
  full_name='harness.Service.Resources',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='requests', full_name='harness.Service.Resources.requests', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='limits', full_name='harness.Service.Resources.limits', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=657,
  serialized_end=756,
)

_SERVICE_CONTAINER = _descriptor.Descriptor(
  name='Container',
  full_name='harness.Service.Container',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='repository', full_name='harness.Service.Container.repository', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='resources', full_name='harness.Service.Container.resources', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\030\001', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=758,
  serialized_end=840,
)

_SERVICE = _descriptor.Descriptor(
  name='Service',
  full_name='harness.Service',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='harness.Service.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='container', full_name='harness.Service.container', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_SERVICE_RESOURCE, _SERVICE_RESOURCES, _SERVICE_CONTAINER, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=544,
  serialized_end=840,
)

_MARK.fields_by_name['protocol'].enum_type = _MARK_PROTOCOL
_MARK_PROTOCOL.containing_type = _MARK
_INPUT.fields_by_name['reach'].enum_type = _INPUT_REACH
_INPUT_REACH.containing_type = _INPUT
_OUTPUT.fields_by_name['expose'].enum_type = _OUTPUT_EXPOSE
_OUTPUT_EXPOSE.containing_type = _OUTPUT
_WIRE.fields_by_name['input'].message_type = _INPUT
_WIRE.fields_by_name['output'].message_type = _OUTPUT
_WIRE.oneofs_by_name['type'].fields.append(
  _WIRE.fields_by_name['input'])
_WIRE.fields_by_name['input'].containing_oneof = _WIRE.oneofs_by_name['type']
_WIRE.oneofs_by_name['type'].fields.append(
  _WIRE.fields_by_name['output'])
_WIRE.fields_by_name['output'].containing_oneof = _WIRE.oneofs_by_name['type']
_SERVICE_RESOURCE.containing_type = _SERVICE
_SERVICE_RESOURCES.fields_by_name['requests'].message_type = _SERVICE_RESOURCE
_SERVICE_RESOURCES.fields_by_name['limits'].message_type = _SERVICE_RESOURCE
_SERVICE_RESOURCES.containing_type = _SERVICE
_SERVICE_CONTAINER.fields_by_name['resources'].message_type = _SERVICE_RESOURCES
_SERVICE_CONTAINER.containing_type = _SERVICE
_SERVICE.fields_by_name['container'].message_type = _SERVICE_CONTAINER
DESCRIPTOR.message_types_by_name['Mark'] = _MARK
DESCRIPTOR.message_types_by_name['Input'] = _INPUT
DESCRIPTOR.message_types_by_name['Output'] = _OUTPUT
DESCRIPTOR.message_types_by_name['Wire'] = _WIRE
DESCRIPTOR.message_types_by_name['Service'] = _SERVICE
DESCRIPTOR.extensions_by_name['wire'] = wire
DESCRIPTOR.extensions_by_name['mark'] = mark
DESCRIPTOR.extensions_by_name['service'] = service
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Mark = _reflection.GeneratedProtocolMessageType('Mark', (_message.Message,), {
  'DESCRIPTOR' : _MARK,
  '__module__' : 'harness.wire_pb2'
  # @@protoc_insertion_point(class_scope:harness.Mark)
  })
_sym_db.RegisterMessage(Mark)

Input = _reflection.GeneratedProtocolMessageType('Input', (_message.Message,), {
  'DESCRIPTOR' : _INPUT,
  '__module__' : 'harness.wire_pb2'
  # @@protoc_insertion_point(class_scope:harness.Input)
  })
_sym_db.RegisterMessage(Input)

Output = _reflection.GeneratedProtocolMessageType('Output', (_message.Message,), {
  'DESCRIPTOR' : _OUTPUT,
  '__module__' : 'harness.wire_pb2'
  # @@protoc_insertion_point(class_scope:harness.Output)
  })
_sym_db.RegisterMessage(Output)

Wire = _reflection.GeneratedProtocolMessageType('Wire', (_message.Message,), {
  'DESCRIPTOR' : _WIRE,
  '__module__' : 'harness.wire_pb2'
  # @@protoc_insertion_point(class_scope:harness.Wire)
  })
_sym_db.RegisterMessage(Wire)

Service = _reflection.GeneratedProtocolMessageType('Service', (_message.Message,), {

  'Resource' : _reflection.GeneratedProtocolMessageType('Resource', (_message.Message,), {
    'DESCRIPTOR' : _SERVICE_RESOURCE,
    '__module__' : 'harness.wire_pb2'
    # @@protoc_insertion_point(class_scope:harness.Service.Resource)
    })
  ,

  'Resources' : _reflection.GeneratedProtocolMessageType('Resources', (_message.Message,), {
    'DESCRIPTOR' : _SERVICE_RESOURCES,
    '__module__' : 'harness.wire_pb2'
    # @@protoc_insertion_point(class_scope:harness.Service.Resources)
    })
  ,

  'Container' : _reflection.GeneratedProtocolMessageType('Container', (_message.Message,), {
    'DESCRIPTOR' : _SERVICE_CONTAINER,
    '__module__' : 'harness.wire_pb2'
    # @@protoc_insertion_point(class_scope:harness.Service.Container)
    })
  ,
  'DESCRIPTOR' : _SERVICE,
  '__module__' : 'harness.wire_pb2'
  # @@protoc_insertion_point(class_scope:harness.Service)
  })
_sym_db.RegisterMessage(Service)
_sym_db.RegisterMessage(Service.Resource)
_sym_db.RegisterMessage(Service.Resources)
_sym_db.RegisterMessage(Service.Container)

wire.message_type = _WIRE
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(wire)
mark.message_type = _MARK
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(mark)
service.message_type = _SERVICE
google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(service)

_INPUT.fields_by_name['type']._options = None
_OUTPUT.fields_by_name['type']._options = None
_WIRE.oneofs_by_name['type']._options = None
_SERVICE_CONTAINER.fields_by_name['resources']._options = None
# @@protoc_insertion_point(module_scope)
