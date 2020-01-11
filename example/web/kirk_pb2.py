# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: kirk.proto

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
from harness import net_pb2 as harness_dot_net__pb2
from harness import http_pb2 as harness_dot_http__pb2
from harness import grpc_pb2 as harness_dot_grpc__pb2
from harness import logging_pb2 as harness_dot_logging__pb2
from harness import tracing_pb2 as harness_dot_tracing__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='kirk.proto',
  package='kirk',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\nkirk.proto\x12\x04kirk\x1a\x12harness/wire.proto\x1a\x16harness/postgres.proto\x1a\x11harness/net.proto\x1a\x12harness/http.proto\x1a\x12harness/grpc.proto\x1a\x15harness/logging.proto\x1a\x15harness/tracing.proto\"\xe8\x04\n\rConfiguration\x12\r\n\x05\x64\x65\x62ug\x18\x01 \x01(\x08\x12Q\n\x02\x64\x62\x18\x02 \x01(\x0b\x32\x1c.harness.postgres.ConnectionB\'\x8a}\x1f\n\x1dpython/asyncpg:ConnectionWire\x8a}\x02(\x03\x12\x46\n\x06scotty\x18\x03 \x01(\x0b\x32\x15.harness.grpc.ChannelB\x1f\x8a}\x1c\n\x1apython/grpclib:ChannelWire\x12J\n\x07\x63onsole\x18\x04 \x01(\x0b\x32\x18.harness.logging.ConsoleB\x1f\x8a}\x1c\n\x1apython/logging:ConsoleWire\x12g\n\x07tracing\x18\x05 \x01(\x0b\x32\x19.harness.tracing.ExporterB;\x8a}8\n6python/opentelemetry.ext.jaeger:JaegerSpanExporterWire\x12N\n\x06server\x18\x06 \x01(\x0b\x32\x14.harness.http.ServerB(\x8a}\x1b\x12\x19python/aiohttp:ServerWire\x8a}\x02\x18\x03\x8a}\x02 \x01\x12M\n\x07monitor\x18\x07 \x01(\x0b\x32\x13.harness.net.ServerB\'\x8a}\x1f\x12\x1dpython/aiomonitor:MonitorWire\x8a}\x02 \x01:Y\x8a}\t\n\x07whisper\x8a}\x02\x10\x01\x8a} \x1a\x1eregistry.acme.dev/team/whisper\x8a}\x11\"\x0f\n\r\n\x04\x33\x30\x30m\x12\x05\x31\x32\x38Mi\x8a}\x0e\"\x0c\x12\n\n\x01\x31\x12\x05\x31\x39\x32Mib\x06proto3')
  ,
  dependencies=[harness_dot_wire__pb2.DESCRIPTOR,harness_dot_postgres__pb2.DESCRIPTOR,harness_dot_net__pb2.DESCRIPTOR,harness_dot_http__pb2.DESCRIPTOR,harness_dot_grpc__pb2.DESCRIPTOR,harness_dot_logging__pb2.DESCRIPTOR,harness_dot_tracing__pb2.DESCRIPTOR,])




_CONFIGURATION = _descriptor.Descriptor(
  name='Configuration',
  full_name='kirk.Configuration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='debug', full_name='kirk.Configuration.debug', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='db', full_name='kirk.Configuration.db', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\037\n\035python/asyncpg:ConnectionWire\212}\002(\003'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='scotty', full_name='kirk.Configuration.scotty', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\034\n\032python/grpclib:ChannelWire'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='console', full_name='kirk.Configuration.console', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\034\n\032python/logging:ConsoleWire'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tracing', full_name='kirk.Configuration.tracing', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}8\n6python/opentelemetry.ext.jaeger:JaegerSpanExporterWire'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='server', full_name='kirk.Configuration.server', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212}\033\022\031python/aiohttp:ServerWire\212}\002\030\003\212}\002 \001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='monitor', full_name='kirk.Configuration.monitor', index=6,
      number=7, type=11, cpp_type=10, label=1,
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
  serialized_options=_b('\212}\t\n\007whisper\212}\002\020\001\212} \032\036registry.acme.dev/team/whisper\212}\021\"\017\n\r\n\004300m\022\005128Mi\212}\016\"\014\022\n\n\0011\022\005192Mi'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=170,
  serialized_end=786,
)

_CONFIGURATION.fields_by_name['db'].message_type = harness_dot_postgres__pb2._CONNECTION
_CONFIGURATION.fields_by_name['scotty'].message_type = harness_dot_grpc__pb2._CHANNEL
_CONFIGURATION.fields_by_name['console'].message_type = harness_dot_logging__pb2._CONSOLE
_CONFIGURATION.fields_by_name['tracing'].message_type = harness_dot_tracing__pb2._EXPORTER
_CONFIGURATION.fields_by_name['server'].message_type = harness_dot_http__pb2._SERVER
_CONFIGURATION.fields_by_name['monitor'].message_type = harness_dot_net__pb2._SERVER
DESCRIPTOR.message_types_by_name['Configuration'] = _CONFIGURATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Configuration = _reflection.GeneratedProtocolMessageType('Configuration', (_message.Message,), {
  'DESCRIPTOR' : _CONFIGURATION,
  '__module__' : 'kirk_pb2'
  # @@protoc_insertion_point(class_scope:kirk.Configuration)
  })
_sym_db.RegisterMessage(Configuration)


_CONFIGURATION.fields_by_name['db']._options = None
_CONFIGURATION.fields_by_name['scotty']._options = None
_CONFIGURATION.fields_by_name['console']._options = None
_CONFIGURATION.fields_by_name['tracing']._options = None
_CONFIGURATION.fields_by_name['server']._options = None
_CONFIGURATION.fields_by_name['monitor']._options = None
_CONFIGURATION._options = None
# @@protoc_insertion_point(module_scope)