# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: harness/net.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from harness import wire_pb2 as harness_dot_wire__pb2
from validate import validate_pb2 as validate_dot_validate__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='harness/net.proto',
  package='harness.net',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x11harness/net.proto\x12\x0bharness.net\x1a\x12harness/wire.proto\x1a\x17validate/validate.proto\"6\n\x06Socket\x12\x15\n\x04host\x18\x01 \x01(\tB\x07\xfa\x42\x04r\x02\x10\x01\x12\x15\n\x04port\x18\x02 \x01(\rB\x07\xfa\x42\x04*\x02 \x00\"\"\n\x04Pipe\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04mode\x18\x02 \x01(\r\"H\n\x07\x41\x64\x64ress\x12%\n\x06socket\x18\x01 \x01(\x0b\x32\x13.harness.net.SocketH\x00\x12\x0e\n\x04pipe\x18\x02 \x01(\tH\x00\x42\x06\n\x04type\"2\n\x06Server\x12(\n\x04\x62ind\x18\x01 \x01(\x0b\x32\x13.harness.net.SocketB\x05\x92}\x02\x08\x00\x62\x06proto3'
  ,
  dependencies=[harness_dot_wire__pb2.DESCRIPTOR,validate_dot_validate__pb2.DESCRIPTOR,])




_SOCKET = _descriptor.Descriptor(
  name='Socket',
  full_name='harness.net.Socket',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='host', full_name='harness.net.Socket.host', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\004r\002\020\001', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='port', full_name='harness.net.Socket.port', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\004*\002 \000', file=DESCRIPTOR),
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
  serialized_start=79,
  serialized_end=133,
)


_PIPE = _descriptor.Descriptor(
  name='Pipe',
  full_name='harness.net.Pipe',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='harness.net.Pipe.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mode', full_name='harness.net.Pipe.mode', index=1,
      number=2, type=13, cpp_type=3, label=1,
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
  serialized_start=135,
  serialized_end=169,
)


_ADDRESS = _descriptor.Descriptor(
  name='Address',
  full_name='harness.net.Address',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='socket', full_name='harness.net.Address.socket', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pipe', full_name='harness.net.Address.pipe', index=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='type', full_name='harness.net.Address.type',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=171,
  serialized_end=243,
)


_SERVER = _descriptor.Descriptor(
  name='Server',
  full_name='harness.net.Server',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='bind', full_name='harness.net.Server.bind', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\222}\002\010\000', file=DESCRIPTOR),
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
  serialized_start=245,
  serialized_end=295,
)

_ADDRESS.fields_by_name['socket'].message_type = _SOCKET
_ADDRESS.oneofs_by_name['type'].fields.append(
  _ADDRESS.fields_by_name['socket'])
_ADDRESS.fields_by_name['socket'].containing_oneof = _ADDRESS.oneofs_by_name['type']
_ADDRESS.oneofs_by_name['type'].fields.append(
  _ADDRESS.fields_by_name['pipe'])
_ADDRESS.fields_by_name['pipe'].containing_oneof = _ADDRESS.oneofs_by_name['type']
_SERVER.fields_by_name['bind'].message_type = _SOCKET
DESCRIPTOR.message_types_by_name['Socket'] = _SOCKET
DESCRIPTOR.message_types_by_name['Pipe'] = _PIPE
DESCRIPTOR.message_types_by_name['Address'] = _ADDRESS
DESCRIPTOR.message_types_by_name['Server'] = _SERVER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Socket = _reflection.GeneratedProtocolMessageType('Socket', (_message.Message,), {
  'DESCRIPTOR' : _SOCKET,
  '__module__' : 'harness.net_pb2'
  # @@protoc_insertion_point(class_scope:harness.net.Socket)
  })
_sym_db.RegisterMessage(Socket)

Pipe = _reflection.GeneratedProtocolMessageType('Pipe', (_message.Message,), {
  'DESCRIPTOR' : _PIPE,
  '__module__' : 'harness.net_pb2'
  # @@protoc_insertion_point(class_scope:harness.net.Pipe)
  })
_sym_db.RegisterMessage(Pipe)

Address = _reflection.GeneratedProtocolMessageType('Address', (_message.Message,), {
  'DESCRIPTOR' : _ADDRESS,
  '__module__' : 'harness.net_pb2'
  # @@protoc_insertion_point(class_scope:harness.net.Address)
  })
_sym_db.RegisterMessage(Address)

Server = _reflection.GeneratedProtocolMessageType('Server', (_message.Message,), {
  'DESCRIPTOR' : _SERVER,
  '__module__' : 'harness.net_pb2'
  # @@protoc_insertion_point(class_scope:harness.net.Server)
  })
_sym_db.RegisterMessage(Server)


_SOCKET.fields_by_name['host']._options = None
_SOCKET.fields_by_name['port']._options = None
_SERVER.fields_by_name['bind']._options = None
# @@protoc_insertion_point(module_scope)
