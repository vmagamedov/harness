# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: harness/tracing.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from harness import net_pb2 as harness_dot_net__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='harness/tracing.proto',
  package='harness.tracing',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x15harness/tracing.proto\x12\x0fharness.tracing\x1a\x11harness/net.proto\"F\n\x08\x45xporter\x12\x14\n\x0cservice_name\x18\x01 \x01(\t\x12$\n\x07\x61\x64\x64ress\x18\x02 \x01(\x0b\x32\x13.harness.net.Socketb\x06proto3')
  ,
  dependencies=[harness_dot_net__pb2.DESCRIPTOR,])




_EXPORTER = _descriptor.Descriptor(
  name='Exporter',
  full_name='harness.tracing.Exporter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='service_name', full_name='harness.tracing.Exporter.service_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='address', full_name='harness.tracing.Exporter.address', index=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=61,
  serialized_end=131,
)

_EXPORTER.fields_by_name['address'].message_type = harness_dot_net__pb2._SOCKET
DESCRIPTOR.message_types_by_name['Exporter'] = _EXPORTER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Exporter = _reflection.GeneratedProtocolMessageType('Exporter', (_message.Message,), {
  'DESCRIPTOR' : _EXPORTER,
  '__module__' : 'harness.tracing_pb2'
  # @@protoc_insertion_point(class_scope:harness.tracing.Exporter)
  })
_sym_db.RegisterMessage(Exporter)


# @@protoc_insertion_point(module_scope)