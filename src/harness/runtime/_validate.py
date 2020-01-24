import re
from abc import ABC, abstractmethod
from typing import Union

from google.protobuf.descriptor import Descriptor, FieldDescriptor
from grpclib.plugin.main import Buffer

from validate import validate_pb2


class ValidationFailed(ValueError):
    pass


class WellKnown:

    def check_email(self, field_name, value: str):
        raise NotImplementedError('Not implemented')

    def check_hostname(self, field_name, value: str):
        raise NotImplementedError('Not implemented')

    def check_ip(self, field_name, value: Union[str, bytes]):
        raise NotImplementedError('Not implemented')

    def check_ipv4(self, field_name, value: Union[str, bytes]):
        raise NotImplementedError('Not implemented')

    def check_ipv6(self, field_name, value: Union[str, bytes]):
        raise NotImplementedError('Not implemented')

    def check_uri(self, field_name, value: str):
        raise NotImplementedError('Not implemented')

    def check_uri_ref(self, field_name, value: str):
        raise NotImplementedError('Not implemented')

    def check_address(self, field_name, value: str):
        raise NotImplementedError('Not implemented')

    def check_uuid(self, field_name, value: str):
        raise NotImplementedError('Not implemented')


CTX = {
    're': re,
    'ValidationFailed': ValidationFailed,
    'wk': WellKnown(),
}


def err_gen(buf, message):
    buf.add(f'raise ValidationFailed({message!r})')


class FieldVisitor(ABC):

    def __init__(self, buf: Buffer, field_name: str) -> None:
        self.buf = buf
        self.field_name = field_name

    @property
    @abstractmethod
    def rule_descriptor(self) -> Descriptor:
        pass

    def dispatch(self, rules):
        for field in self.rule_descriptor.fields:
            rule_value = getattr(rules, field.name)
            if field.label == FieldDescriptor.LABEL_REPEATED:
                if not rule_value:
                    continue
            else:
                if not rules.HasField(field.name):
                    continue
            try:
                visit_fn = getattr(self, f'visit_{field.name}')
            except AttributeError:
                # FIXME: remove this when all validators implemented
                continue
            visit_fn(rule_value)


class ConstMixin:
    buf: Buffer
    field_name: str

    def visit_const(self, value):
        self.buf.add(f'if p.{self.field_name} != {value}:')
        with self.buf.indent():
            err_gen(self.buf,
                    f'{self.field_name} length does not equal {value}')


class InMixin:
    buf: Buffer
    field_name: str

    def visit_in(self, value):
        self.buf.add(f'if p.{self.field_name} not in {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} not in {value}')

    def visit_not_in(self, value):
        self.buf.add(f'if p.{self.field_name} in {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} in {value}')


class ComparatorMixin:
    buf: Buffer
    field_name: str

    def visit_lt(self, value):
        self.buf.add(f'if not p.{self.field_name} < {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} is not lesser than {value}')

    def visit_lte(self, value):
        self.buf.add(f'if not p.{self.field_name} <= {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} is not lesser than or equal to {value}')

    def visit_gt(self, value):
        self.buf.add(f'if not p.{self.field_name} > {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} is not greater than {value}')

    def visit_gte(self, value):
        self.buf.add(f'if not p.{self.field_name} >= {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} is not greater than or equal to {value}')


class SizableMixin:
    buf: Buffer
    field_name: str

    def visit_len(self, value):
        self.buf.add(f'if len(p.{self.field_name}) != {value}:')
        with self.buf.indent():
            err_gen(self.buf,
                    f'{self.field_name} length does not equal {value}')

    def visit_min_len(self, value):
        self.buf.add(f'if len(p.{self.field_name}) < {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} length is less than {value}')

    def visit_max_len(self, value):
        self.buf.add(f'if len(p.{self.field_name}) > {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} length is more than {value}')


class Float(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.FloatRules.DESCRIPTOR


class Double(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.DoubleRules.DESCRIPTOR


class Int32(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.Int32Rules.DESCRIPTOR


class Int64(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.Int64Rules.DESCRIPTOR


class UInt32(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.UInt32Rules.DESCRIPTOR


class UInt64(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.UInt64Rules.DESCRIPTOR


class SInt32(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.SInt32Rules.DESCRIPTOR


class SInt64(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.SInt64Rules.DESCRIPTOR


class Fixed32(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.Fixed32Rules.DESCRIPTOR


class Fixed64(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.Fixed64Rules.DESCRIPTOR


class SFixed32(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.SFixed32Rules.DESCRIPTOR


class SFixed64(ConstMixin, InMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.SFixed64Rules.DESCRIPTOR


class Bool(ConstMixin, FieldVisitor):
    rule_descriptor = validate_pb2.BoolRules.DESCRIPTOR


class CommonString:
    buf: Buffer
    field_name: str

    def visit_prefix(self, value):
        self.buf.add(f'if not p.{self.field_name}.startswith({value}):')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} does not start with prefix {value}')

    def visit_suffix(self, value):
        self.buf.add(f'if not p.{self.field_name}.endswith({value}):')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} does not end with suffix {value}')

    def visit_contains(self, value):
        self.buf.add(f'if {value} not in p.{self.field_name}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} does not contain {value}')

    def visit_not_contains(self, value):
        self.buf.add(f'if {value} in p.{self.field_name}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} contains {value}')


class String(CommonString, ConstMixin, InMixin, SizableMixin, FieldVisitor):
    rule_descriptor = validate_pb2.StringRules.DESCRIPTOR

    def visit_len_bytes(self, value):
        self.buf.add(f'if len(p.{self.field_name}.encode("utf-8")) != {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} bytes count does not equal {value}')

    def visit_min_bytes(self, value):
        self.buf.add(f'if len(p.{self.field_name}.encode("utf-8")) < {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} bytes count is less than {value}')

    def visit_max_bytes(self, value):
        self.buf.add(f'if len(p.{self.field_name}.encode("utf-8")) > {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} bytes count is more than {value}')

    def visit_pattern(self, value):
        self.buf.add(f'if re.search({value}, p.{self.field_name}) is None:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.field_name} does not match pattern {value}')

    def visit_email(self, _):
        self.buf.add(f'wk.check_email(p.{self.field_name})')

    def visit_hostname(self, _):
        self.buf.add(f'wk.check_hostname(p.{self.field_name})')

    def visit_ip(self, _):
        self.buf.add(f'wk.check_ip(p.{self.field_name})')

    def visit_ipv4(self, _):
        self.buf.add(f'wk.check_ipv4(p.{self.field_name})')

    def visit_ipv6(self, _):
        self.buf.add(f'wk.check_ipv6(p.{self.field_name})')

    def visit_uri(self, _):
        self.buf.add(f'wk.check_uri(p.{self.field_name})')

    def visit_uri_ref(self, _):
        self.buf.add(f'wk.check_uri_ref(p.{self.field_name})')

    def visit_address(self, _):
        self.buf.add(f'wk.check_address(p.{self.field_name})')

    def visit_uuid(self, _):
        self.buf.add(f'wk.check_uuid(p.{self.field_name})')


class Bytes(CommonString, ConstMixin, InMixin, SizableMixin, FieldVisitor):
    rule_descriptor = validate_pb2.BytesRules.DESCRIPTOR

    def visit_pattern(self, value):
        try:
            value_bytes = value.encode('ascii')
        except UnicodeEncodeError:
            err_gen(self.buf, f'{self.field_name} has invalid validation pattern {value}')
        else:
            self.buf.add(f'if re.search({value_bytes!r}, p.{self.field_name}) is None:')
            with self.buf.indent():
                err_gen(self.buf, f'{self.field_name} does not match pattern {value_bytes!r}')

    def visit_ip(self, _):
        self.buf.add(f'wk.check_ip(p.{self.field_name})')

    def visit_ipv4(self, _):
        self.buf.add(f'wk.check_ipv4(p.{self.field_name})')

    def visit_ipv6(self, _):
        self.buf.add(f'wk.check_ipv6(p.{self.field_name})')


TYPES = {r.rule_descriptor.full_name: r for r in [
    Float,
    Double,
    Int32,
    Int64,
    UInt32,
    UInt64,
    SInt32,
    SInt64,
    Fixed32,
    Fixed64,
    SFixed32,
    SFixed64,
    Bool,
    String,
    Bytes,
]}


def field_gen(buf, field):
    if field.message_type is None:
        for opt, opt_value in field.GetOptions().ListFields():
            if opt.full_name == "validate.rules":
                type_ = opt_value.WhichOneof('type')
                rule_value = getattr(opt_value, type_)
                generator = TYPES[rule_value.DESCRIPTOR.full_name]
                generator(buf, field.name).dispatch(rule_value)
    else:
        pass


def file_gen(message):
    buf = Buffer()
    buf.add('def validate(p):')
    initial_size = len(buf._lines)
    with buf.indent():
        for opt, opt_value in message.DESCRIPTOR.GetOptions().ListFields():
            if opt.full_name == "validate.disabled" and opt_value:
                buf.add('return')
                return
        for oneof in message.DESCRIPTOR.oneofs:
            buf.add(f"__{oneof.name} = p.WhichOneof('{oneof.name}')")
            for i, field in enumerate(oneof.fields):
                ctrl = 'elif' if i else 'if'
                buf.add(f"{ctrl} __{oneof.name} == '{field.name}':")
                with buf.indent():
                    field_gen(buf, field)
            for opt, opt_value in oneof.GetOptions().ListFields():
                if opt.name == 'required' and opt_value:
                    buf.add(f"else:")
                    with buf.indent():
                        err_gen(buf, f'Oneof {oneof.name} is required')
        for field in message.DESCRIPTOR.fields:
            if not field.containing_oneof:
                field_gen(buf, field)
        if len(buf._lines) == initial_size:
            buf.add('pass')
    return buf.content()
