# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: kirk.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from validate import validate_pb2 as validate_dot_validate__pb2
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
  serialized_pb=b'\n\nkirk.proto\x12\x04kirk\x1a\x17validate/validate.proto\x1a\x12harness/wire.proto\x1a\x16harness/postgres.proto\x1a\x11harness/net.proto\x1a\x12harness/http.proto\x1a\x12harness/grpc.proto\x1a\x15harness/logging.proto\x1a\x15harness/tracing.proto\"\x9e\x05\n\rConfiguration\x12\r\n\x05\x64\x65\x62ug\x18\x01 \x01(\x08\x12X\n\x02\x64\x62\x18\x02 \x01(\x0b\x32\x16.harness.postgres.PoolB4\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}\"\n \n\x1eharness.wires.asyncpg.PoolWire\x8a}\x04\n\x02\x10\x03\x12\x65\n\x06scotty\x18\x03 \x01(\x0b\x32\x15.harness.grpc.ChannelB>\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a},\n*\n(harness.wires.grpclib.client.ChannelWire\x8a}\x04\n\x02\x10\x01\x12[\n\x07\x63onsole\x18\x04 \x01(\x0b\x32\x18.harness.logging.ConsoleB0\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}%\n#\n!harness.wires.logging.ConsoleWire\x12v\n\x07tracing\x18\x05 \x01(\x0b\x32\x17.harness.tracing.JaegerBL\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}A\n?\n=harness.wires.opentelemetry.ext.jaeger.JaegerSpanExporterWire\x12`\n\x06server\x18\x06 \x01(\x0b\x32\x14.harness.http.ServerB:\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}(\x12&\n$harness.wires.aiohttp.web.ServerWire\x8a}\x04\x12\x02\x10\x03\x12Y\n\x07monitor\x18\x07 \x01(\x0b\x32\x13.harness.net.ServerB3\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}(\x12&\n$harness.wires.aiomonitor.MonitorWire:+\x8a}\x06\n\x04kirk\x8a}\x1f\x12\x1d\n\x1bregistry.acme.dev/team/kirkb\x06proto3'
  ,
  dependencies=[validate_dot_validate__pb2.DESCRIPTOR,harness_dot_wire__pb2.DESCRIPTOR,harness_dot_postgres__pb2.DESCRIPTOR,harness_dot_net__pb2.DESCRIPTOR,harness_dot_http__pb2.DESCRIPTOR,harness_dot_grpc__pb2.DESCRIPTOR,harness_dot_logging__pb2.DESCRIPTOR,harness_dot_tracing__pb2.DESCRIPTOR,])




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
      serialized_options=b'\372B\005\212\001\002\020\001\212}\"\n \n\036harness.wires.asyncpg.PoolWire\212}\004\n\002\020\003', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='scotty', full_name='kirk.Configuration.scotty', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212},\n*\n(harness.wires.grpclib.client.ChannelWire\212}\004\n\002\020\001', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='console', full_name='kirk.Configuration.console', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212}%\n#\n!harness.wires.logging.ConsoleWire', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tracing', full_name='kirk.Configuration.tracing', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212}A\n?\n=harness.wires.opentelemetry.ext.jaeger.JaegerSpanExporterWire', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='server', full_name='kirk.Configuration.server', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212}(\022&\n$harness.wires.aiohttp.web.ServerWire\212}\004\022\002\020\003', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='monitor', full_name='kirk.Configuration.monitor', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212}(\022&\n$harness.wires.aiomonitor.MonitorWire', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\212}\006\n\004kirk\212}\037\022\035\n\033registry.acme.dev/team/kirk',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=195,
  serialized_end=865,
)

_CONFIGURATION.fields_by_name['db'].message_type = harness_dot_postgres__pb2._POOL
_CONFIGURATION.fields_by_name['scotty'].message_type = harness_dot_grpc__pb2._CHANNEL
_CONFIGURATION.fields_by_name['console'].message_type = harness_dot_logging__pb2._CONSOLE
_CONFIGURATION.fields_by_name['tracing'].message_type = harness_dot_tracing__pb2._JAEGER
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
