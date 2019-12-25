# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: svc.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from harness import wire_pb2 as harness_dot_wire__pb2
from harness import postgres_pb2 as harness_dot_postgres__pb2
from harness import http_pb2 as harness_dot_http__pb2
from harness import logging_pb2 as harness_dot_logging__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='svc.proto',
  package='example',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\tsvc.proto\x12\x07\x65xample\x1a\x12harness/wire.proto\x1a\x16harness/postgres.proto\x1a\x12harness/http.proto\x1a\x15harness/logging.proto\"\x8e\x03\n\rConfiguration\x12\r\n\x05\x64\x65\x62ug\x18\x01 \x01(\x08\x12L\n\x02\x64\x62\x18\x02 \x01(\x0b\x32\x1c.harness.postgres.ConnectionB\"\x8a}\x1f\n\x1dpython/asyncpg:ConnectionWire\x12J\n\x07\x63onsole\x18\x03 \x01(\x0b\x32\x18.harness.logging.ConsoleB\x1f\x8a}\x1c\n\x1apython/logging:ConsoleWire\x12N\n\x06server\x18\x04 \x01(\x0b\x32\x14.harness.http.ServerB(\x8a}\x1b\x12\x19python/aiohttp:ServerWire\x8a}\x02\x18\x03\x8a}\x02 \x01\x12N\n\x07monitor\x18\x05 \x01(\x0b\x32\x14.harness.http.ServerB\'\x8a}\x1f\x12\x1dpython/aiomonitor:MonitorWire\x8a}\x02 \x01:4\x8a}\t\n\x07whisper\x8a}\x02\x10\x01\x8a} \x1a\x1eregistry.acme.dev/team/whisperb\x06proto3')
  ,
  dependencies=[harness_dot_wire__pb2.DESCRIPTOR,harness_dot_postgres__pb2.DESCRIPTOR,harness_dot_http__pb2.DESCRIPTOR,harness_dot_logging__pb2.DESCRIPTOR,])




_CONFIGURATION = _descriptor.Descriptor(
  name='Configuration',
  full_name='example.Configuration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='debug', full_name='example.Configuration.debug', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='db', full_name='example.Configuration.db', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\037\n\035python/asyncpg:ConnectionWire'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='console', full_name='example.Configuration.console', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\034\n\032python/logging:ConsoleWire'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='server', full_name='example.Configuration.server', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\033\022\031python/aiohttp:ServerWire\212}\002\030\003\212}\002 \001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='monitor', full_name='example.Configuration.monitor', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\037\022\035python/aiomonitor:MonitorWire\212}\002 \001'), file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('\212}\t\n\007whisper\212}\002\020\001\212} \032\036registry.acme.dev/team/whisper'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=110,
  serialized_end=508,
)

_CONFIGURATION.fields_by_name['db'].message_type = harness_dot_postgres__pb2._CONNECTION
_CONFIGURATION.fields_by_name['console'].message_type = harness_dot_logging__pb2._CONSOLE
_CONFIGURATION.fields_by_name['server'].message_type = harness_dot_http__pb2._SERVER
_CONFIGURATION.fields_by_name['monitor'].message_type = harness_dot_http__pb2._SERVER
DESCRIPTOR.message_types_by_name['Configuration'] = _CONFIGURATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Configuration = _reflection.GeneratedProtocolMessageType('Configuration', (_message.Message,), {
  'DESCRIPTOR' : _CONFIGURATION,
  '__module__' : 'svc_pb2'
  # @@protoc_insertion_point(class_scope:example.Configuration)
  })
_sym_db.RegisterMessage(Configuration)


_CONFIGURATION.fields_by_name['db']._options = None
_CONFIGURATION.fields_by_name['console']._options = None
_CONFIGURATION.fields_by_name['server']._options = None
_CONFIGURATION.fields_by_name['monitor']._options = None
_CONFIGURATION._options = None
# @@protoc_insertion_point(module_scope)
