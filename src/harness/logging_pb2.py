# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: harness/logging.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='harness/logging.proto',
  package='harness.logging',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x15harness/logging.proto\x12\x0fharness.logging\"\x83\x01\n\x07\x43onsole\x12/\n\x06stream\x18\x01 \x01(\x0e\x32\x1f.harness.logging.Console.Stream\x12%\n\x05level\x18\x02 \x01(\x0e\x32\x16.harness.logging.Level\" \n\x06Stream\x12\n\n\x06STDERR\x10\x00\x12\n\n\x06STDOUT\x10\x01\"\xf3\x01\n\x06Syslog\x12\x0b\n\x03\x61pp\x18\x01 \x01(\t\x12\x32\n\x08\x66\x61\x63ility\x18\x02 \x01(\x0e\x32 .harness.logging.Syslog.Facility\x12%\n\x05level\x18\x03 \x01(\x0e\x32\x16.harness.logging.Level\"\x80\x01\n\x08\x46\x61\x63ility\x12\n\n\x06NOTSET\x10\x00\x12\x08\n\x04USER\x10\x02\x12\n\n\x06LOCAL0\x10\x11\x12\n\n\x06LOCAL1\x10\x12\x12\n\n\x06LOCAL2\x10\x13\x12\n\n\x06LOCAL3\x10\x14\x12\n\n\x06LOCAL4\x10\x15\x12\n\n\x06LOCAL5\x10\x16\x12\n\n\x06LOCAL6\x10\x17\x12\n\n\x06LOCAL7\x10\x18*N\n\x05Level\x12\n\n\x06NOTSET\x10\x00\x12\t\n\x05\x44\x45\x42UG\x10\x01\x12\x08\n\x04INFO\x10\x02\x12\x0b\n\x07WARNING\x10\x03\x12\t\n\x05\x45RROR\x10\x04\x12\x0c\n\x08\x43RITICAL\x10\x05\x62\x06proto3')
)

_LEVEL = _descriptor.EnumDescriptor(
  name='Level',
  full_name='harness.logging.Level',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NOTSET', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DEBUG', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INFO', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WARNING', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ERROR', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CRITICAL', index=5, number=5,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=422,
  serialized_end=500,
)
_sym_db.RegisterEnumDescriptor(_LEVEL)

Level = enum_type_wrapper.EnumTypeWrapper(_LEVEL)
NOTSET = 0
DEBUG = 1
INFO = 2
WARNING = 3
ERROR = 4
CRITICAL = 5


_CONSOLE_STREAM = _descriptor.EnumDescriptor(
  name='Stream',
  full_name='harness.logging.Console.Stream',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STDERR', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STDOUT', index=1, number=1,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=142,
  serialized_end=174,
)
_sym_db.RegisterEnumDescriptor(_CONSOLE_STREAM)

_SYSLOG_FACILITY = _descriptor.EnumDescriptor(
  name='Facility',
  full_name='harness.logging.Syslog.Facility',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NOTSET', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='USER', index=1, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL0', index=2, number=17,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL1', index=3, number=18,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL2', index=4, number=19,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL3', index=5, number=20,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL4', index=6, number=21,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL5', index=7, number=22,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL6', index=8, number=23,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCAL7', index=9, number=24,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=292,
  serialized_end=420,
)
_sym_db.RegisterEnumDescriptor(_SYSLOG_FACILITY)


_CONSOLE = _descriptor.Descriptor(
  name='Console',
  full_name='harness.logging.Console',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='stream', full_name='harness.logging.Console.stream', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='level', full_name='harness.logging.Console.level', index=1,
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
    _CONSOLE_STREAM,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=43,
  serialized_end=174,
)


_SYSLOG = _descriptor.Descriptor(
  name='Syslog',
  full_name='harness.logging.Syslog',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='app', full_name='harness.logging.Syslog.app', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='facility', full_name='harness.logging.Syslog.facility', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='level', full_name='harness.logging.Syslog.level', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SYSLOG_FACILITY,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=177,
  serialized_end=420,
)

_CONSOLE.fields_by_name['stream'].enum_type = _CONSOLE_STREAM
_CONSOLE.fields_by_name['level'].enum_type = _LEVEL
_CONSOLE_STREAM.containing_type = _CONSOLE
_SYSLOG.fields_by_name['facility'].enum_type = _SYSLOG_FACILITY
_SYSLOG.fields_by_name['level'].enum_type = _LEVEL
_SYSLOG_FACILITY.containing_type = _SYSLOG
DESCRIPTOR.message_types_by_name['Console'] = _CONSOLE
DESCRIPTOR.message_types_by_name['Syslog'] = _SYSLOG
DESCRIPTOR.enum_types_by_name['Level'] = _LEVEL
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Console = _reflection.GeneratedProtocolMessageType('Console', (_message.Message,), {
  'DESCRIPTOR' : _CONSOLE,
  '__module__' : 'harness.logging_pb2'
  # @@protoc_insertion_point(class_scope:harness.logging.Console)
  })
_sym_db.RegisterMessage(Console)

Syslog = _reflection.GeneratedProtocolMessageType('Syslog', (_message.Message,), {
  'DESCRIPTOR' : _SYSLOG,
  '__module__' : 'harness.logging_pb2'
  # @@protoc_insertion_point(class_scope:harness.logging.Syslog)
  })
_sym_db.RegisterMessage(Syslog)


# @@protoc_insertion_point(module_scope)
