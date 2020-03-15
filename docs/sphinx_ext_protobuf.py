from docutils.nodes import Element

from sphinx import addnodes
from sphinx.addnodes import pending_xref, desc_signature
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.locale import _
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


SCALARS = {
    "float",
    "double",
    "int32",
    "int64",
    "uint32",
    "uint64",
    "sint32",
    "sint64",
    "fixed32",
    "fixed64",
    "sfixed32",
    "sfixed64",
    "bool",
    "string",
    "bytes",
}


class ProtoPackage(ObjectDescription):
    has_content = False
    required_arguments = 1
    optional_arguments = 0

    def run(self):
        self.env.ref_context["proto:package"] = self.arguments[0]
        return []


class ProtoValue(ObjectDescription):
    def handle_signature(self, sig: str, signode: desc_signature):
        signode += addnodes.desc_name(sig, sig)
        return sig


class ProtoEnum(ObjectDescription):
    def handle_signature(self, sig: str, signode: desc_signature):
        package = self.env.ref_context["proto:package"]
        signode += addnodes.desc_annotation("enum", "enum")
        signode += addnodes.desc_addname(package, package + ".")
        signode += addnodes.desc_name(sig, sig)
        return sig

    def add_target_and_index(self, name, sig: str, signode: desc_signature):
        package = self.env.ref_context["proto:package"]
        message = self.env.ref_context.get("proto:message", None)
        if message is not None:
            targetid = f"{message}.{sig}"
        else:
            targetid = sig
        signode["names"].append(targetid)
        signode["ids"].append(targetid)
        self.state.document.note_explicit_target(signode)
        domain = self.env.get_domain("proto")
        assert isinstance(domain, ProtobufDomain), type(domain)
        target = f"{package}.{targetid}"
        domain.note_type(self.env.docname, target, targetid)


class ProtoField(ObjectDescription):
    _repeated_prefix = "repeated "

    def handle_signature(self, sig: str, signode: desc_signature):
        repeated = False
        if sig.startswith(self._repeated_prefix):
            sig = sig[len(self._repeated_prefix) :]  # noqa
            repeated = True
        type_, name = sig.split()
        signode += addnodes.desc_name(name, name)
        if repeated:
            signode += addnodes.desc_annotation("repeated", "repeated")
        if type_ in SCALARS:
            signode += addnodes.desc_addname(type_, type_)
        else:
            signode += addnodes.pending_xref(
                "",
                addnodes.desc_addname(type_, type_),
                refdomain="proto",
                reftype="message",
                reftarget=type_,
            )
        return sig


class ProtoMessage(ObjectDescription):
    def handle_signature(self, sig: str, signode: desc_signature):
        package = self.env.ref_context["proto:package"]
        signode += addnodes.desc_annotation("message", "message")
        signode += addnodes.desc_addname(package, package + ".")
        signode += addnodes.desc_name(sig, sig)
        return sig

    def before_content(self):
        assert self.names and len(self.names) == 1, self.names
        self.env.ref_context["proto:message"] = self.names[0]

    def after_content(self):
        del self.env.ref_context["proto:message"]

    def add_target_and_index(self, name, sig: str, signode: desc_signature):
        signode["names"].append(sig)
        signode["ids"].append(sig)
        self.state.document.note_explicit_target(signode)

        domain = self.env.get_domain("proto")
        assert isinstance(domain, ProtobufDomain), type(domain)
        package = self.env.ref_context["proto:package"]
        target = f"{package}.{sig}"
        domain.note_type(self.env.docname, target, sig)


class ProtobufDomain(Domain):
    name = "proto"
    label = "Protocol Buffers"
    object_types = {
        "enum": ObjType(_("enum"), "enum"),
        "message": ObjType(_("message"), "message"),
    }
    directives = {
        "package": ProtoPackage,
        "enum": ProtoEnum,
        "value": ProtoValue,
        "message": ProtoMessage,
        "field": ProtoField,
    }
    roles = {
        "enum": XRefRole(),
        "message": XRefRole(),
    }
    initial_data = {
        "types": {},
    }

    def note_type(self, docname, target, target_id):
        self.data["types"][target] = (docname, target_id)

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> Element:
        refdoc, target_id = self.data["types"][target]
        return make_refnode(
            builder,
            fromdocname,
            todocname=refdoc,
            targetid=target_id,
            child=contnode,
            title="",
        )


def setup(app: Sphinx):
    app.add_domain(ProtobufDomain)
