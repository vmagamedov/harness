import re
from abc import ABC, abstractmethod
from typing import Union, List
from decimal import Decimal
from collections import Counter

from grpclib.plugin.main import Buffer
from google.protobuf.message import Message
from google.protobuf.descriptor import Descriptor, FieldDescriptor
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp

from validate import validate_pb2


class ValidationFailed(ValueError):
    pass


class Format:

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


def dec(value: str):
    return Decimal(value)


def dec_repr(value: Union[Timestamp, Duration]):
    return f'{value.seconds}.{value.nanos:09d}'


def sec(value: Union[Timestamp, Duration]):
    return Decimal(dec_repr(value))


def now():
    ts = Timestamp()
    ts.GetCurrentTime()
    return sec(ts)


def err_gen(buf, message, **ctx):
    message_repr = repr(message)
    if ctx:
        ctx_items = ', '.join(
            '{}={}'.format(key, val) for key, val in ctx.items()
        )
        message_repr += f'.format({ctx_items})'
    buf.add(f'raise ValidationFailed({message_repr})')


class FieldVisitor(ABC):

    def __init__(self, buf: Buffer, field: FieldDescriptor, code_path: List[str], proto_path: List[str]) -> None:
        self.buf = buf
        self.field = field
        self.code_path = code_path
        self.proto_path = proto_path

    @property
    @abstractmethod
    def rule_descriptor(self) -> Descriptor:
        pass

    def field_value(self):
        return '.'.join(self.code_path)

    def proto_name(self):
        return ''.join(self.proto_path)

    def rule_value(self, value):
        return repr(value)

    def rule_value_repr(self, value):
        return repr(value)

    def dispatch(self, rules):
        for field in self.rule_descriptor.fields:
            if field.label == FieldDescriptor.LABEL_REPEATED:
                rule_value = getattr(rules, field.name)
                if not rule_value:
                    continue
            else:
                if not rules.HasField(field.name):
                    continue
                rule_value = getattr(rules, field.name)
            try:
                visit_fn = getattr(self, f'visit_{field.name}')
            except AttributeError:
                raise NotImplementedError(field.full_name)
            visit_fn(rule_value)


class ConstMixin:
    buf: Buffer
    field_name: str

    def visit_const(self, value):
        self.buf.add(f'if {self.field_value()} != {self.rule_value(value)}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} not equal to {self.rule_value_repr(value)}')


class InMixin:
    buf: Buffer
    field_name: str

    def _set(self, value):
        return '{{' + ', '.join([self.rule_value(i) for i in value]) + '}}'

    def _set_repr(self, value):
        return '{{' + ', '.join([self.rule_value_repr(i) for i in value]) + '}}'

    def visit_in(self, value):
        value_set = self._set(value)
        value_set_repr = self._set_repr(value)
        self.buf.add(f'if {self.field_value()} not in {value_set}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} not in {value_set_repr}')

    def visit_not_in(self, value):
        value_set = self._set(value)
        value_set_repr = self._set_repr(value)
        self.buf.add(f'if {self.field_value()} in {value_set}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} in {value_set_repr}')


class ComparatorMixin:
    buf: Buffer
    field_name: str

    def visit_lt(self, value):
        self.buf.add(f'if not {self.field_value()} < {self.rule_value(value)}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is not lesser than {self.rule_value_repr(value)}')

    def visit_lte(self, value):
        self.buf.add(f'if not {self.field_value()} <= {self.rule_value(value)}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is not lesser than or equal to {self.rule_value_repr(value)}')

    def visit_gt(self, value):
        self.buf.add(f'if not {self.field_value()} > {self.rule_value(value)}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is not greater than {self.rule_value_repr(value)}')

    def visit_gte(self, value):
        self.buf.add(f'if not {self.field_value()} >= {self.rule_value(value)}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is not greater than or equal to {self.rule_value_repr(value)}')


class SizableMixin:
    buf: Buffer
    field_name: str

    def visit_len(self, value):
        self.buf.add(f'if len({self.field_value()}) != {value}:')
        with self.buf.indent():
            err_gen(self.buf,
                    f'{self.proto_name()} length does not equal {value}')

    def visit_min_len(self, value):
        self.buf.add(f'if len({self.field_value()}) < {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} length is less than {value}')

    def visit_max_len(self, value):
        self.buf.add(f'if len({self.field_value()}) > {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} length is more than {value}')


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
        self.buf.add(f'if not {self.field_value()}.startswith({value}):')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} does not start with prefix {value}')

    def visit_suffix(self, value):
        self.buf.add(f'if not {self.field_value()}.endswith({value}):')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} does not end with suffix {value}')

    def visit_contains(self, value):
        self.buf.add(f'if {value} not in {self.field_value()}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} does not contain {value}')

    def visit_not_contains(self, value):
        self.buf.add(f'if {value} in {self.field_value()}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} contains {value}')


class String(CommonString, ConstMixin, InMixin, SizableMixin, FieldVisitor):
    rule_descriptor = validate_pb2.StringRules.DESCRIPTOR

    def visit_len_bytes(self, value):
        self.buf.add(f'if len({self.field_value()}.encode("utf-8")) != {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} bytes count does not equal {value}')

    def visit_min_bytes(self, value):
        self.buf.add(f'if len({self.field_value()}.encode("utf-8")) < {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} bytes count is less than {value}')

    def visit_max_bytes(self, value):
        self.buf.add(f'if len({self.field_value()}.encode("utf-8")) > {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} bytes count is more than {value}')

    def visit_pattern(self, value):
        self.buf.add(f'if re.search({value}, {self.field_value()}) is None:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} does not match pattern {value}')

    def visit_email(self, _):
        self.buf.add(f'fmt.check_email({self.field_value()})')

    def visit_hostname(self, _):
        self.buf.add(f'fmt.check_hostname({self.field_value()})')

    def visit_ip(self, _):
        self.buf.add(f'fmt.check_ip({self.field_value()})')

    def visit_ipv4(self, _):
        self.buf.add(f'fmt.check_ipv4({self.field_value()})')

    def visit_ipv6(self, _):
        self.buf.add(f'fmt.check_ipv6({self.field_value()})')

    def visit_uri(self, _):
        self.buf.add(f'fmt.check_uri({self.field_value()})')

    def visit_uri_ref(self, _):
        self.buf.add(f'fmt.check_uri_ref({self.field_value()})')

    def visit_address(self, _):
        self.buf.add(f'fmt.check_address({self.field_value()})')

    def visit_uuid(self, _):
        self.buf.add(f'fmt.check_uuid({self.field_value()})')


class Bytes(CommonString, ConstMixin, InMixin, SizableMixin, FieldVisitor):
    rule_descriptor = validate_pb2.BytesRules.DESCRIPTOR

    def visit_pattern(self, value):
        try:
            value_bytes = value.encode('ascii')
        except UnicodeEncodeError:
            err_gen(self.buf, f'{self.proto_name()} has invalid validation pattern {value}')
        else:
            self.buf.add(f'if re.search({value_bytes!r}, {self.field_value()}) is None:')
            with self.buf.indent():
                err_gen(self.buf, f'{self.proto_name()} does not match pattern {value_bytes!r}')

    def visit_ip(self, _):
        self.buf.add(f'fmt.check_ip({self.field_value()})')

    def visit_ipv4(self, _):
        self.buf.add(f'fmt.check_ipv4({self.field_value()})')

    def visit_ipv6(self, _):
        self.buf.add(f'fmt.check_ipv6({self.field_value()})')


class EnumRules(ConstMixin, InMixin, FieldVisitor):
    rule_descriptor = validate_pb2.EnumRules.DESCRIPTOR

    def visit_defined_only(self, _):
        ids = [e.number for e in self.field.enum_type.values]
        ids_repr = '{{' + ', '.join(map(repr, ids)) + '}}'
        self.buf.add(f'if {self.field_value()} not in {ids_repr}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is not defined')


class RepeatedRules(FieldVisitor):
    rule_descriptor = validate_pb2.RepeatedRules.DESCRIPTOR

    def visit_min_items(self, value: int):
        self.buf.add(f'if len({self.field_value()}) < {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} items count is less than {value}')

    def visit_max_items(self, value: int):
        self.buf.add(f'if len({self.field_value()}) > {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} items count is more than {value}')

    def visit_unique(self, _):
        self.buf.add(f'if len(set({self.field_value()})) < len({self.field_value()}):')
        with self.buf.indent():
            repeated = f'[i for i, count in Counter({self.field_value()}).items() if count > 1]'
            err_gen(self.buf, f'{self.proto_name()} must contain unique items; repeated items: {{{{repeated}}}}', repeated=repeated)

    def visit_items(self, value: validate_pb2.FieldRules):
        self.buf.add(f'for item in {self.field_value()}:')
        with self.buf.indent():
            proto_path = self.proto_path + ['[]']
            dispatch_field(self.buf, self.field, ['item'], proto_path, value)


class MapRules(FieldVisitor):
    rule_descriptor = validate_pb2.MapRules.DESCRIPTOR

    def visit_min_pairs(self, value: int):
        self.buf.add(f'if len({self.field_value()}) < {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} needs to contain at least {value} items')

    def visit_max_pairs(self, value: int):
        self.buf.add(f'if len({self.field_value()}) > {value}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} can contain at most {value} items')

    def visit_no_sparse(self, _):
        # no_sparse validation is not implemented because protobuf maps
        # cannot be sparse in Python
        pass

    def visit_keys(self, value: validate_pb2.FieldRules):
        self.buf.add(f'for key in {self.field_value()}.keys():')
        with self.buf.indent():
            proto_path = self.proto_path + ['<key>']
            dispatch_field(self.buf, self.field, ['key'], proto_path, value)

    def visit_values(self, value: validate_pb2.FieldRules):
        self.buf.add(f'for value in {self.field_value()}.values():')
        with self.buf.indent():
            proto_path = self.proto_path + ['<value>']
            dispatch_field(self.buf, self.field, ['value'], proto_path, value)


class MessageMixin:
    buf: Buffer
    field_name: str

    def visit_required(self, _):
        has_field = '.'.join(self.path + ['HasField'])
        self.buf.add(f'if not {has_field}("{self.field_name}"):')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is required')


class MessageRules(MessageMixin, FieldVisitor):
    rule_descriptor = validate_pb2.MessageRules.DESCRIPTOR

    def visit_skip(self, _):
        # This option is handled explicitly outside
        pass


class AnyRules(MessageMixin, InMixin, FieldVisitor):
    rule_descriptor = validate_pb2.AnyRules.DESCRIPTOR

    def field_value(self):
        return f'{super().field_value()}.type_url'

    def proto_name(self):
        return f'{super().proto_name()}.type_url'

    def visit_in(self, value):
        self.buf.add('print(p.field.type_url)')
        value_set = self._set(value)
        value_set_repr = self._set_repr(value)
        self.buf.add(f'if {self.field_value()} not in {value_set}:')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} not in {value_set_repr}')


class TimeCoerce:

    def field_value(self):
        return f'sec({super().field_value()})'

    def rule_value(self, value):
        return f'dec("{dec_repr(value)}")'

    def rule_value_repr(self, value):
        return value.ToJsonString()


class DurationRules(TimeCoerce, MessageMixin, ConstMixin, ComparatorMixin, InMixin, FieldVisitor):
    rule_descriptor = validate_pb2.DurationRules.DESCRIPTOR


class TimestampRules(TimeCoerce, MessageMixin, ConstMixin, ComparatorMixin, FieldVisitor):
    rule_descriptor = validate_pb2.TimestampRules.DESCRIPTOR

    lt_now: bool
    gt_now: bool

    def visit_lt_now(self, _):
        pass

    def visit_gt_now(self, _):
        pass

    def visit_within(self, value):
        if self.lt_now:
            self.visit_within_past(value)
        elif self.gt_now:
            self.visit_within_future(value)
        else:
            self.buf.add(f'if not abs({self.field_value()} - now()) < {self.rule_value(value)}:')
            with self.buf.indent():
                err_gen(self.buf, f'{self.proto_name()} is not within {self.rule_value_repr(value)} from now')

    def visit_within_past(self, value):
        self.buf.add(f'if not (0 < now() - {self.field_value()} < {self.rule_value(value)}):')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is not within {self.rule_value_repr(value)} in the past')

    def visit_within_future(self, value):
        self.buf.add(f'if not (0 < {self.field_value()} - now() < {self.rule_value(value)}):')
        with self.buf.indent():
            err_gen(self.buf, f'{self.proto_name()} is not within {self.rule_value_repr(value)} in the future')

    def dispatch(self, rules):
        self.lt_now = rules.lt_now
        self.gt_now = rules.gt_now
        super().dispatch(rules)


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
    EnumRules,
    RepeatedRules,
    MapRules,
    AnyRules,
    DurationRules,
    TimestampRules,
]}


def dispatch_field(buf, field, code_path, proto_path, opt_value):
    if opt_value.HasField('message'):
        assert field.message_type
        if opt_value.message.skip:
            return
        else:
            MessageRules(buf, field.name).dispatch(opt_value.message)
    oneof_type = opt_value.WhichOneof('type')
    if oneof_type:
        rule_value = getattr(opt_value, oneof_type)
        generator = TYPES[rule_value.DESCRIPTOR.full_name]
        generator(buf, field, code_path, proto_path).dispatch(rule_value)


def field_gen(buf, field, code_path, proto_path):
    for opt, opt_value in field.GetOptions().ListFields():
        if opt.full_name == "validate.rules":
            dispatch_field(buf, field, code_path, proto_path, opt_value)
            if opt_value.HasField('message'):
                if opt_value.message.skip:
                    return

    if field.message_type:
        for opt, opt_value in field.message_type.GetOptions().ListFields():
            if opt.full_name == 'google.protobuf.MessageOptions.map_entry' and opt_value is True:
                return
        field_value = '.'.join(code_path)
        if field.label == FieldDescriptor.LABEL_REPEATED:
            buf.add(f'for item in {field_value}:')
            with buf.indent():
                buf.add(f'validate(item)')
        else:
            buf.add(f'if {field_value} is not None:')
            with buf.indent():
                buf.add(f'validate({field_value})')


def file_gen(message):
    buf = Buffer()
    buf.add('def _validate(p):')
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
                    field_gen(buf, field, ['p', field.name], [field.name])
            for opt, opt_value in oneof.GetOptions().ListFields():
                if opt.name == 'required' and opt_value:
                    buf.add(f"else:")
                    with buf.indent():
                        err_gen(buf, f'Oneof {oneof.name} is required')
        for field in message.DESCRIPTOR.fields:
            if not field.containing_oneof:
                field_gen(buf, field, ['p', field.name], [field.name])
        if len(buf._lines) == initial_size:
            buf.add('pass')
    return buf.content()


_validators = {}


def validate(message: Message):
    key = message.DESCRIPTOR.full_name
    func = _validators.get(key, None)
    if func is None:
        locals_ = {}
        source = file_gen(message)
        exec(source, CTX, locals_)
        func = _validators[key] = locals_['_validate']
    return func(message)


CTX = {
    're': re,
    'ValidationFailed': ValidationFailed,
    'fmt': Format(),
    'sec': sec,
    'now': now,
    'dec': dec,
    'Counter': Counter,
    'validate': validate,
}
