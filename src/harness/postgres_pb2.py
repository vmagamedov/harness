# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: harness/postgres.proto

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
  name='harness/postgres.proto',
  package='harness.postgres',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x16harness/postgres.proto\x12\x10harness.postgres\x1a\x11harness/net.proto\"h\n\nConnection\x12$\n\x07\x61\x64\x64ress\x18\x01 \x01(\x0b\x32\x13.harness.net.Socket\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\x12\x10\n\x08\x64\x61tabase\x18\x04 \x01(\tb\x06proto3')
  ,
  dependencies=[harness_dot_net__pb2.DESCRIPTOR,])




_CONNECTION = _descriptor.Descriptor(
  name='Connection',
  full_name='harness.postgres.Connection',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='harness.postgres.Connection.address', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='username', full_name='harness.postgres.Connection.username', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='password', full_name='harness.postgres.Connection.password', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='database', full_name='harness.postgres.Connection.database', index=3,
      number=4, type=9, cpp_type=9, label=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=63,
  serialized_end=167,
)

_CONNECTION.fields_by_name['address'].message_type = harness_dot_net__pb2._SOCKET
DESCRIPTOR.message_types_by_name['Connection'] = _CONNECTION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Connection = _reflection.GeneratedProtocolMessageType('Connection', (_message.Message,), {
  'DESCRIPTOR' : _CONNECTION,
  '__module__' : 'harness.postgres_pb2'
  # @@protoc_insertion_point(class_scope:harness.postgres.Connection)
  })
_sym_db.RegisterMessage(Connection)


# @@protoc_insertion_point(module_scope)
