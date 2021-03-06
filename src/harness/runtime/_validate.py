import re
import ipaddress
from abc import ABC
from typing import TYPE_CHECKING, Union, List, Any, Dict, Collection, AnyStr, Optional
from typing import Callable, ClassVar
from decimal import Decimal
from collections import Counter
from urllib.parse import urlparse
from email.headerregistry import AddressHeader

from google.protobuf.message import Message
from google.protobuf.descriptor import Descriptor, FieldDescriptor
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp

from validate import validate_pb2

from ._utils import Buffer

if TYPE_CHECKING:
    from typing_extensions import Literal, TypedDict


class ValidationError(ValueError):
    pass


class Format:
    # Based on Django 3.0.2: django.core.validators.URLValidator
    _scheme = r"^(?:[a-z0-9\.\-\+]*)://"
    _user = r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"
    _ipv4 = r"(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}"
    _ipv6 = r"\[[0-9a-f:\.]+\]"  # (simple regex, validated later)
    _host = (
        r"("
        # hostname
        r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        # domain
        r"(?:\.(?!-)[a-z0-9-]{1,63}(?<!-))*"
        # tld
        r"\.(?!-)(?:[a-z-]{2,63})(?<!-)\.?"
        # special
        r"|localhost)"
    )
    _addr = r"(?:" + _ipv4 + "|" + _ipv6 + "|" + _host + ")"
    _port = r"(?::\d{2,5})?"
    _resource = r"(?:[/?#][^\s]*)?"
    _uri = _scheme + _user + _addr + _port + _resource
    _uri_ref = r"(?:" + _scheme + _user + _addr + _port + ")?" + _resource

    _host_re = re.compile("^" + _host + "$", re.IGNORECASE)
    _uri_re = re.compile("^" + _uri + "$", re.IGNORECASE)
    _uri_ref_re = re.compile("^" + _uri_ref + "$", re.IGNORECASE)

    _uuid_re = re.compile(
        "^[0-9a-f]{8}" "-[0-9a-f]{4}" "-[0-9a-f]{4}" "-[0-9a-f]{4}" "-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    def check_email(self, field_name: str, value: str) -> None:
        result: Dict[str, Any] = {}
        AddressHeader.parse(value, result)
        defects = result["defects"]
        if defects:
            errors = "\n".join(f" - {str(defect)}" for defect in defects)
            raise ValidationError(
                f"{field_name} contains invalid email address:\n{errors}"
            )

        groups = result["groups"]
        if len(groups) > 1 or len(groups[0].addresses) > 1:
            raise ValidationError(f"{field_name} contains more than one email address")

    def check_hostname(self, field_name: str, value: str) -> None:
        if self._host_re.match(value) is None:
            raise ValidationError(f"{field_name} contains invalid hostname")

    def check_ip(self, field_name: str, value: Union[str, bytes]) -> None:
        try:
            ipaddress.ip_address(value)
        except ValueError:
            raise ValidationError(f"{field_name} contains invalid IP address") from None

    def check_ipv4(self, field_name: str, value: Union[str, bytes]) -> None:
        try:
            ipaddress.IPv4Address(value)
        except ValueError:
            raise ValidationError(
                f"{field_name} contains invalid IPv4 address"
            ) from None

    def check_ipv6(self, field_name: str, value: Union[str, bytes]) -> None:
        try:
            ipaddress.IPv6Address(value)
        except ValueError:
            raise ValidationError(
                f"{field_name} contains invalid IPv6 address"
            ) from None

    def check_uri(self, field_name: str, value: str) -> None:
        if not self._uri_re.match(value):
            raise ValidationError(f"{field_name} contains invalid URI")
        url = urlparse(value)
        assert url.hostname, url
        self.check_address(field_name, url.hostname)

    def check_uri_ref(self, field_name: str, value: str) -> None:
        if not self._uri_ref_re.match(value):
            raise ValidationError(f"{field_name} contains invalid URI-reference")
        url = urlparse(value)
        if url.hostname:
            self.check_address(field_name, url.hostname)

    def check_address(self, field_name: str, value: str) -> None:
        if self._host_re.match(value) is None:
            try:
                ipaddress.ip_address(value)
                return
            except ValueError:
                pass
        else:
            return
        raise ValidationError(f"{field_name} contains invalid address")

    def check_uuid(self, field_name: str, value: str) -> None:
        if self._uuid_re.match(value) is None:
            raise ValidationError(f"{field_name} contains invalid UUID") from None


_AnyTime = Union[Timestamp, Duration]


def dec(value: str) -> Decimal:
    return Decimal(value)


def dec_repr(value: _AnyTime) -> str:
    return f"{value.seconds}.{value.nanos:09d}"


def sec(value: _AnyTime) -> Decimal:
    return Decimal(dec_repr(value))


def now() -> Decimal:
    ts = Timestamp()
    ts.GetCurrentTime()
    return sec(ts)


def err_gen(buf: Buffer, message: str, **ctx: str) -> None:
    message_repr = repr(message)
    if ctx:
        ctx_items = ", ".join("{}={}".format(key, val) for key, val in ctx.items())
        message_repr += f".format({ctx_items})"
    buf.add(f"raise {ValidationError.__name__}({message_repr})")


class FieldRulesBase:
    buf: Buffer
    field: FieldDescriptor
    code_path: List[str]
    proto_path: List[str]

    def field_value(self) -> str:
        return ".".join(self.code_path)

    def proto_name(self) -> str:
        return "".join(self.proto_path)

    def rule_value(self, value: Any) -> str:
        return repr(value)

    def rule_value_repr(self, value: Any) -> str:
        return repr(value)


class FieldRules(FieldRulesBase, ABC):
    rule_descriptor: ClassVar[Descriptor]

    def __init__(
        self,
        buf: Buffer,
        field: FieldDescriptor,
        code_path: List[str],
        proto_path: List[str],
    ) -> None:
        self.buf = buf
        self.field = field
        self.code_path = code_path
        self.proto_path = proto_path

    def dispatch(self, rules: Message) -> None:
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
                visit_fn = getattr(self, f"visit_{field.name}")
            except AttributeError:
                raise NotImplementedError(field.full_name)
            visit_fn(rule_value)


class ConstRulesMixin(FieldRulesBase):
    def visit_const(self, value: Any) -> None:
        self.buf.add(f"if {self.field_value()} != {self.rule_value(value)}:")
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} not equal to {self.rule_value_repr(value)}",
            )


class InRulesMixin(FieldRulesBase):
    def _set(self, value: Collection[Any]) -> str:
        return "{{" + ", ".join([self.rule_value(i) for i in value]) + "}}"

    def _set_repr(self, value: Collection[Any]) -> str:
        return "{{" + ", ".join([self.rule_value_repr(i) for i in value]) + "}}"

    def visit_in(self, value: Collection[Any]) -> None:
        value_set = self._set(value)
        value_set_repr = self._set_repr(value)
        self.buf.add(f"if {self.field_value()} not in {value_set}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} not in {value_set_repr}")

    def visit_not_in(self, value: Collection[Any]) -> None:
        value_set = self._set(value)
        value_set_repr = self._set_repr(value)
        self.buf.add(f"if {self.field_value()} in {value_set}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} in {value_set_repr}")


class ComparatorRulesMixin(FieldRulesBase):
    def visit_lt(self, value: Any) -> None:
        self.buf.add(f"if not {self.field_value()} < {self.rule_value(value)}:")
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} is not lesser than {self.rule_value_repr(value)}",
            )

    def visit_lte(self, value: Any) -> None:
        self.buf.add(f"if not {self.field_value()} <= {self.rule_value(value)}:")
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} is not"
                f" lesser than or equal to {self.rule_value_repr(value)}",
            )

    def visit_gt(self, value: Any) -> None:
        self.buf.add(f"if not {self.field_value()} > {self.rule_value(value)}:")
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} is not"
                f" greater than {self.rule_value_repr(value)}",
            )

    def visit_gte(self, value: Any) -> None:
        self.buf.add(f"if not {self.field_value()} >= {self.rule_value(value)}:")
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} is not"
                f" greater than or equal to {self.rule_value_repr(value)}",
            )


class SizableRulesMixin(FieldRulesBase):
    def visit_len(self, value: Collection[Any]) -> None:
        self.buf.add(f"if len({self.field_value()}) != {value}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} length does not equal {value}")

    def visit_min_len(self, value: Collection[Any]) -> None:
        self.buf.add(f"if len({self.field_value()}) < {value}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} length is less than {value}")

    def visit_max_len(self, value: Collection[Any]) -> None:
        self.buf.add(f"if len({self.field_value()}) > {value}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} length is more than {value}")


class FloatRules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.FloatRules.DESCRIPTOR


class DoubleRules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.DoubleRules.DESCRIPTOR


class Int32Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.Int32Rules.DESCRIPTOR


class Int64Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.Int64Rules.DESCRIPTOR


class UInt32Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.UInt32Rules.DESCRIPTOR


class UInt64Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.UInt64Rules.DESCRIPTOR


class SInt32Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.SInt32Rules.DESCRIPTOR


class SInt64Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.SInt64Rules.DESCRIPTOR


class Fixed32Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.Fixed32Rules.DESCRIPTOR


class Fixed64Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.Fixed64Rules.DESCRIPTOR


class SFixed32Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.SFixed32Rules.DESCRIPTOR


class SFixed64Rules(ConstRulesMixin, InRulesMixin, ComparatorRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.SFixed64Rules.DESCRIPTOR


class BoolRules(ConstRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.BoolRules.DESCRIPTOR


class CommonStringRules(FieldRulesBase):
    def visit_prefix(self, value: AnyStr) -> None:
        self.buf.add(
            f"if not {self.field_value()}.startswith({self.rule_value(value)}):"
        )
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} does not start with"
                f" prefix {self.rule_value_repr(value)}",
            )

    def visit_suffix(self, value: AnyStr) -> None:
        self.buf.add(f"if not {self.field_value()}.endswith({self.rule_value(value)}):")
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} does not end with"
                f" suffix {self.rule_value_repr(value)}",
            )

    def visit_contains(self, value: AnyStr) -> None:
        self.buf.add(f"if {self.rule_value(value)} not in {self.field_value()}:")
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} does not contain {self.rule_value_repr(value)}",
            )

    def visit_not_contains(self, value: AnyStr) -> None:
        self.buf.add(f"if {self.rule_value(value)} in {self.field_value()}:")
        with self.buf.indent():
            err_gen(
                self.buf, f"{self.proto_name()} contains {self.rule_value_repr(value)}"
            )


class StringRules(
    CommonStringRules, ConstRulesMixin, InRulesMixin, SizableRulesMixin, FieldRules
):
    rule_descriptor = validate_pb2.StringRules.DESCRIPTOR

    def visit_len_bytes(self, value: str) -> None:
        self.buf.add(
            f'if len({self.field_value()}.encode("utf-8")) != {self.rule_value(value)}:'
        )
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} bytes count does not"
                f" equal {self.rule_value_repr(value)}",
            )

    def visit_min_bytes(self, value: str) -> None:
        self.buf.add(
            f'if len({self.field_value()}.encode("utf-8")) < {self.rule_value(value)}:'
        )
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} bytes count is less"
                f" than {self.rule_value_repr(value)}",
            )

    def visit_max_bytes(self, value: str) -> None:
        self.buf.add(
            f'if len({self.field_value()}.encode("utf-8")) > {self.rule_value(value)}:'
        )
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} bytes count is more"
                f" than {self.rule_value_repr(value)}",
            )

    def visit_pattern(self, value: str) -> None:
        self.buf.add(
            f"if re.search({self.rule_value(value)}, {self.field_value()}) is None:"
        )
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} does not match"
                f" pattern {self.rule_value_repr(value)}",
            )

    def visit_email(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_email({self.proto_name()!r}, {self.field_value()})")

    def visit_hostname(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_hostname({self.proto_name()!r}, {self.field_value()})")

    def visit_ip(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_ip({self.proto_name()!r}, {self.field_value()})")

    def visit_ipv4(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_ipv4({self.proto_name()!r}, {self.field_value()})")

    def visit_ipv6(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_ipv6({self.proto_name()!r}, {self.field_value()})")

    def visit_uri(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_uri({self.proto_name()!r}, {self.field_value()})")

    def visit_uri_ref(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_uri_ref({self.proto_name()!r}, {self.field_value()})")

    def visit_address(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_address({self.proto_name()!r}, {self.field_value()})")

    def visit_uuid(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_uuid({self.proto_name()!r}, {self.field_value()})")


class BytesRules(
    CommonStringRules, ConstRulesMixin, InRulesMixin, SizableRulesMixin, FieldRules
):
    rule_descriptor = validate_pb2.BytesRules.DESCRIPTOR

    def visit_pattern(self, value: str) -> None:
        try:
            value_bytes = value.encode("ascii")
        except UnicodeEncodeError:
            err_gen(
                self.buf, f"{self.proto_name()} has invalid validation pattern {value}"
            )
        else:
            self.buf.add(
                f"if re.search({self.rule_value(value_bytes)},"
                f" {self.field_value()}) is None:"
            )
            with self.buf.indent():
                err_gen(
                    self.buf,
                    f"{self.proto_name()} does not match"
                    f" pattern {self.rule_value_repr(value_bytes)}",
                )

    def visit_ip(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_ip({self.proto_name()!r}, {self.field_value()})")

    def visit_ipv4(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_ipv4({self.proto_name()!r}, {self.field_value()})")

    def visit_ipv6(self, _: "Literal[True]") -> None:
        self.buf.add(f"fmt.check_ipv6({self.proto_name()!r}, {self.field_value()})")


class EnumRules(ConstRulesMixin, InRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.EnumRules.DESCRIPTOR

    def visit_defined_only(self, _: "Literal[True]") -> None:
        ids = [e.number for e in self.field.enum_type.values]
        ids_repr = "{{" + ", ".join(map(repr, ids)) + "}}"
        self.buf.add(f"if {self.field_value()} not in {ids_repr}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} is not defined")


class RepeatedRules(FieldRules):
    rule_descriptor = validate_pb2.RepeatedRules.DESCRIPTOR

    def visit_min_items(self, value: int) -> None:
        self.buf.add(f"if len({self.field_value()}) < {value}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} items count is less than {value}")

    def visit_max_items(self, value: int) -> None:
        self.buf.add(f"if len({self.field_value()}) > {value}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} items count is more than {value}")

    def visit_unique(self, _: "Literal[True]") -> None:
        self.buf.add(f"if len(set({self.field_value()})) < len({self.field_value()}):")
        with self.buf.indent():
            repeated = (
                f"[i for i, count in Counter({self.field_value()}).items()"
                f" if count > 1]"
            )
            err_gen(
                self.buf,
                f"{self.proto_name()} must contain unique items;"
                f" repeated items: {{{{repeated}}}}",
                repeated=repeated,
            )

    def visit_items(self, value: validate_pb2.FieldRules) -> None:
        self.buf.add(f"for item in {self.field_value()}:")
        with self.buf.indent():
            proto_path = self.proto_path + ["[]"]
            dispatch_field(self.buf, self.field, ["item"], proto_path, value)


class MapRules(FieldRules):
    rule_descriptor = validate_pb2.MapRules.DESCRIPTOR

    def visit_min_pairs(self, value: int) -> None:
        self.buf.add(f"if len({self.field_value()}) < {value}:")
        with self.buf.indent():
            err_gen(
                self.buf, f"{self.proto_name()} needs to contain at least {value} items"
            )

    def visit_max_pairs(self, value: int) -> None:
        self.buf.add(f"if len({self.field_value()}) > {value}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} can contain at most {value} items")

    def visit_no_sparse(self, _: "Literal[True]") -> None:
        # no_sparse validation is not implemented because protobuf maps
        # cannot be sparse in Python
        pass

    def visit_keys(self, value: validate_pb2.FieldRules) -> None:
        self.buf.add(f"for key in {self.field_value()}.keys():")
        with self.buf.indent():
            proto_path = self.proto_path + ["<key>"]
            dispatch_field(self.buf, self.field, ["key"], proto_path, value)

    def visit_values(self, value: validate_pb2.FieldRules) -> None:
        self.buf.add(f"for value in {self.field_value()}.values():")
        with self.buf.indent():
            proto_path = self.proto_path + ["<value>"]
            dispatch_field(self.buf, self.field, ["value"], proto_path, value)


class MessageRulesMixin(FieldRulesBase):
    def visit_required(self, _: "Literal[True]") -> None:
        container = ".".join(self.code_path[:-1])
        field_name = self.code_path[-1]
        self.buf.add(f"if not {container}.HasField({field_name!r}):")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} is required")


class MessageRules(MessageRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.MessageRules.DESCRIPTOR

    def visit_skip(self, _: "Literal[True]") -> None:
        # This option is handled explicitly outside
        pass


class AnyRules(MessageRulesMixin, InRulesMixin, FieldRules):
    rule_descriptor = validate_pb2.AnyRules.DESCRIPTOR

    def field_value(self) -> str:
        return f"{super().field_value()}.type_url"

    def proto_name(self) -> str:
        return f"{super().proto_name()}.type_url"

    def visit_in(self, value: Collection[Any]) -> None:
        self.buf.add("print(p.field.type_url)")
        value_set = self._set(value)
        value_set_repr = self._set_repr(value)
        self.buf.add(f"if {self.field_value()} not in {value_set}:")
        with self.buf.indent():
            err_gen(self.buf, f"{self.proto_name()} not in {value_set_repr}")


class TimeFormatMixin(FieldRulesBase):
    def field_value(self) -> str:
        return f"sec({super().field_value()})"

    def rule_value(self, value: _AnyTime) -> str:
        return f'dec("{dec_repr(value)}")'

    def rule_value_repr(self, value: _AnyTime) -> str:
        return value.ToJsonString()


class DurationRules(
    TimeFormatMixin,
    MessageRulesMixin,
    ConstRulesMixin,
    ComparatorRulesMixin,
    InRulesMixin,
    FieldRules,
):
    rule_descriptor = validate_pb2.DurationRules.DESCRIPTOR


class TimestampRules(
    TimeFormatMixin,
    MessageRulesMixin,
    ConstRulesMixin,
    ComparatorRulesMixin,
    FieldRules,
):
    rule_descriptor = validate_pb2.TimestampRules.DESCRIPTOR

    lt_now: bool
    gt_now: bool

    def visit_lt_now(self, _: "Literal[True]") -> None:
        # this rule is used only in conjunction with "within" rule, and handled
        # in visit_within method
        pass

    def visit_gt_now(self, _: "Literal[True]") -> None:
        # this rule is used only in conjunction with "within" rule, and handled
        # in visit_within method
        pass

    def visit_within(self, value: Duration) -> None:
        if self.lt_now:
            self._visit_within_past(value)
        elif self.gt_now:
            self._visit_within_future(value)
        else:
            self.buf.add(
                f"if not abs({self.field_value()} - now()) < {self.rule_value(value)}:"
            )
            with self.buf.indent():
                err_gen(
                    self.buf,
                    f"{self.proto_name()} is not"
                    f" within {self.rule_value_repr(value)} from now",
                )

    def _visit_within_past(self, value: Duration) -> None:
        self.buf.add(
            f"if not (0 < now() - {self.field_value()} < {self.rule_value(value)}):"
        )
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} is not"
                f" within {self.rule_value_repr(value)} in the past",
            )

    def _visit_within_future(self, value: Duration) -> None:
        self.buf.add(
            f"if not (0 < {self.field_value()} - now() < {self.rule_value(value)}):"
        )
        with self.buf.indent():
            err_gen(
                self.buf,
                f"{self.proto_name()} is not"
                f" within {self.rule_value_repr(value)} in the future",
            )

    def dispatch(self, rules: Message) -> None:
        assert isinstance(rules, validate_pb2.TimestampRules)
        self.lt_now = rules.lt_now
        self.gt_now = rules.gt_now
        super().dispatch(rules)


FIELD_RULE_TYPES: Dict[str, type] = {
    r.rule_descriptor.full_name: r
    for r in [
        FloatRules,
        DoubleRules,
        Int32Rules,
        Int64Rules,
        UInt32Rules,
        UInt64Rules,
        SInt32Rules,
        SInt64Rules,
        Fixed32Rules,
        Fixed64Rules,
        SFixed32Rules,
        SFixed64Rules,
        BoolRules,
        StringRules,
        BytesRules,
        EnumRules,
        RepeatedRules,
        MapRules,
        AnyRules,
        DurationRules,
        TimestampRules,
    ]
}


def dispatch_field(
    buf: Buffer,
    field: FieldDescriptor,
    code_path: List[str],
    proto_path: List[str],
    opt_value: validate_pb2.FieldRules,
) -> None:
    if opt_value.HasField("message"):
        assert field.message_type
        MessageRules(buf, field, code_path, proto_path).dispatch(opt_value.message)
    oneof_type = opt_value.WhichOneof("type")
    if oneof_type:
        rule_value = getattr(opt_value, oneof_type)
        generator = FIELD_RULE_TYPES[rule_value.DESCRIPTOR.full_name]
        generator(buf, field, code_path, proto_path).dispatch(rule_value)


def field_gen(
    buf: Buffer, field: FieldDescriptor, code_path: List[str], proto_path: List[str]
) -> None:
    for opt, opt_value in field.GetOptions().ListFields():
        if opt.full_name == "validate.rules":
            dispatch_field(buf, field, code_path, proto_path, opt_value)
            if opt_value.HasField("message"):
                assert field.message_type
                if opt_value.message.skip:
                    return

    if field.message_type:
        for opt, opt_value in field.message_type.GetOptions().ListFields():
            if (
                opt.full_name == "google.protobuf.MessageOptions.map_entry"
                and opt_value is True
            ):
                return
        field_value = ".".join(code_path)
        if field.label == FieldDescriptor.LABEL_REPEATED:
            buf.add(f"for item in {field_value}:")
            with buf.indent():
                buf.add("validate(item)")
        else:
            outer = ".".join(code_path[:-1])
            inner = code_path[-1]
            buf.add(f'if {outer}.HasField("{inner}"):')
            with buf.indent():
                buf.add(f"validate({field_value})")


def file_gen(message: Message) -> Optional[str]:
    for opt, opt_value in message.DESCRIPTOR.GetOptions().ListFields():
        if opt.full_name == "validate.disabled" and opt_value:
            return None

    buf = Buffer()
    buf.add("def _validate(p):")
    pos = buf.position
    with buf.indent():
        for oneof in message.DESCRIPTOR.oneofs:
            buf.add(f"__{oneof.name} = p.WhichOneof('{oneof.name}')")
            for i, field in enumerate(oneof.fields):
                ctrl = "elif" if i else "if"
                buf.add(f"{ctrl} __{oneof.name} == '{field.name}':")
                with buf.indent():
                    inner_pos = buf.position
                    field_gen(buf, field, ["p", field.name], [field.name])
                    if buf.position == inner_pos:
                        buf.add("pass")
            for opt, opt_value in oneof.GetOptions().ListFields():
                if opt.name == "required" and opt_value:
                    buf.add("else:")
                    with buf.indent():
                        err_gen(buf, f"Oneof {oneof.name} is required")
        for field in message.DESCRIPTOR.fields:
            if not field.containing_oneof:
                field_gen(buf, field, ["p", field.name], [field.name])
        if buf.position == pos:
            buf.add("pass")
    return buf.content()


def _validate_disabled(message: Message) -> None:
    pass


_validators: Dict[str, Callable[[Message], None]] = {}


if TYPE_CHECKING:

    class _Locals(TypedDict):
        _validate: Optional[Callable[[Message], None]]


def validate(message: Message) -> None:
    key = message.DESCRIPTOR.full_name
    func = _validators.get(key, None)
    if func is None:
        source = file_gen(message)
        if source is not None:
            locals_: "_Locals" = {"_validate": None}
            exec(source, CTX, locals_)
            func = locals_["_validate"]
            assert func is not None
        else:
            func = _validate_disabled
        _validators[key] = func
    func(message)


CTX = {
    "re": re,
    ValidationError.__name__: ValidationError,
    "fmt": Format(),
    "sec": sec,
    "now": now,
    "dec": dec,
    "Counter": Counter,
    validate.__name__: validate,
}
