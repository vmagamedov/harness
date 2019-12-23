# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: harness/wire.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='harness/wire.proto',
  package='harness',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x12harness/wire.proto\x12\x07harness\x1a google/protobuf/descriptor.proto\"8\n\x0bHarnessWire\x12\x0f\n\x05input\x18\x01 \x01(\tH\x00\x12\x10\n\x06output\x18\x02 \x01(\tH\x00\x42\x06\n\x04type:B\n\x04wire\x12\x1d.google.protobuf.FieldOptions\x18\xd1\x0f \x01(\x0b\x32\x14.harness.HarnessWire')
  ,
  dependencies=[google_dot_protobuf_dot_descriptor__pb2.DESCRIPTOR,])


WIRE_FIELD_NUMBER = 2001
wire = _descriptor.FieldDescriptor(
  name='wire', full_name='harness.wire', index=0,
  number=2001, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)


_HARNESSWIRE = _descriptor.Descriptor(
  name='HarnessWire',
  full_name='harness.HarnessWire',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='input', full_name='harness.HarnessWire.input', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='output', full_name='harness.HarnessWire.output', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
      name='type', full_name='harness.HarnessWire.type',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=65,
  serialized_end=121,
)

_HARNESSWIRE.oneofs_by_name['type'].fields.append(
  _HARNESSWIRE.fields_by_name['input'])
_HARNESSWIRE.fields_by_name['input'].containing_oneof = _HARNESSWIRE.oneofs_by_name['type']
_HARNESSWIRE.oneofs_by_name['type'].fields.append(
  _HARNESSWIRE.fields_by_name['output'])
_HARNESSWIRE.fields_by_name['output'].containing_oneof = _HARNESSWIRE.oneofs_by_name['type']
DESCRIPTOR.message_types_by_name['HarnessWire'] = _HARNESSWIRE
DESCRIPTOR.extensions_by_name['wire'] = wire
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

HarnessWire = _reflection.GeneratedProtocolMessageType('HarnessWire', (_message.Message,), {
  'DESCRIPTOR' : _HARNESSWIRE,
  '__module__' : 'harness.wire_pb2'
  # @@protoc_insertion_point(class_scope:harness.HarnessWire)
  })
_sym_db.RegisterMessage(HarnessWire)

wire.message_type = _HARNESSWIRE
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(wire)

# @@protoc_insertion_point(module_scope)