# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: harness/redis.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from harness import wire_pb2 as harness_dot_wire__pb2
from harness import net_pb2 as harness_dot_net__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='harness/redis.proto',
  package='harness.redis',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x13harness/redis.proto\x12\rharness.redis\x1a\x12harness/wire.proto\x1a\x11harness/net.proto\"E\n\nConnection\x12+\n\x07\x61\x64\x64ress\x18\x01 \x01(\x0b\x32\x13.harness.net.SocketB\x05\x8a}\x02 \x00\x12\n\n\x02\x64\x62\x18\x02 \x01(\x05\x62\x06proto3'
  ,
  dependencies=[harness_dot_wire__pb2.DESCRIPTOR,harness_dot_net__pb2.DESCRIPTOR,])




_CONNECTION = _descriptor.Descriptor(
  name='Connection',
  full_name='harness.redis.Connection',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='harness.redis.Connection.address', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\212}\002 \000', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='db', full_name='harness.redis.Connection.db', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=77,
  serialized_end=146,
)

_CONNECTION.fields_by_name['address'].message_type = harness_dot_net__pb2._SOCKET
DESCRIPTOR.message_types_by_name['Connection'] = _CONNECTION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Connection = _reflection.GeneratedProtocolMessageType('Connection', (_message.Message,), {
  'DESCRIPTOR' : _CONNECTION,
  '__module__' : 'harness.redis_pb2'
  # @@protoc_insertion_point(class_scope:harness.redis.Connection)
  })
_sym_db.RegisterMessage(Connection)


_CONNECTION.fields_by_name['address']._options = None
# @@protoc_insertion_point(module_scope)
