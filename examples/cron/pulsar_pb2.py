# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pulsar.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from validate import validate_pb2 as validate_dot_validate__pb2
from harness import wire_pb2 as harness_dot_wire__pb2
from harness import redis_pb2 as harness_dot_redis__pb2
from harness import logging_pb2 as harness_dot_logging__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pulsar.proto',
  package='pulsar',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x0cpulsar.proto\x12\x06pulsar\x1a\x17validate/validate.proto\x1a\x12harness/wire.proto\x1a\x13harness/redis.proto\x1a\x15harness/logging.proto\x1a\x1bgoogle/protobuf/empty.proto\"\xdc\x02\n\rConfiguration\x12~\n\x0fredis_job_store\x18\x01 \x01(\x0b\x32\x19.harness.redis.ConnectionBJ\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}?\n=\n;harness.wires.apscheduler.jobstores.redis.RedisJobStoreWire\x12[\n\x07\x63onsole\x18\x02 \x01(\x0b\x32\x18.harness.logging.ConsoleB0\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}%\n#\n!harness.wires.logging.ConsoleWire\x12\x61\n\tscheduler\x18\x03 \x01(\x0b\x32\x16.google.protobuf.EmptyB6\xfa\x42\x05\x8a\x01\x02\x10\x01\x8a}+\x12)\n\'harness.wires.apscheduler.SchedulerWire:\x0b\x8a}\x08\n\x06pulsarb\x06proto3'
  ,
  dependencies=[validate_dot_validate__pb2.DESCRIPTOR,harness_dot_wire__pb2.DESCRIPTOR,harness_dot_redis__pb2.DESCRIPTOR,harness_dot_logging__pb2.DESCRIPTOR,google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_CONFIGURATION = _descriptor.Descriptor(
  name='Configuration',
  full_name='pulsar.Configuration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='redis_job_store', full_name='pulsar.Configuration.redis_job_store', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212}?\n=\n;harness.wires.apscheduler.jobstores.redis.RedisJobStoreWire', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='console', full_name='pulsar.Configuration.console', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212}%\n#\n!harness.wires.logging.ConsoleWire', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='scheduler', full_name='pulsar.Configuration.scheduler', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\372B\005\212\001\002\020\001\212}+\022)\n\'harness.wires.apscheduler.SchedulerWire', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'\212}\010\n\006pulsar',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=143,
  serialized_end=491,
)

_CONFIGURATION.fields_by_name['redis_job_store'].message_type = harness_dot_redis__pb2._CONNECTION
_CONFIGURATION.fields_by_name['console'].message_type = harness_dot_logging__pb2._CONSOLE
_CONFIGURATION.fields_by_name['scheduler'].message_type = google_dot_protobuf_dot_empty__pb2._EMPTY
DESCRIPTOR.message_types_by_name['Configuration'] = _CONFIGURATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Configuration = _reflection.GeneratedProtocolMessageType('Configuration', (_message.Message,), {
  'DESCRIPTOR' : _CONFIGURATION,
  '__module__' : 'pulsar_pb2'
  # @@protoc_insertion_point(class_scope:pulsar.Configuration)
  })
_sym_db.RegisterMessage(Configuration)


_CONFIGURATION.fields_by_name['redis_job_store']._options = None
_CONFIGURATION.fields_by_name['console']._options = None
_CONFIGURATION.fields_by_name['scheduler']._options = None
_CONFIGURATION._options = None
# @@protoc_insertion_point(module_scope)
