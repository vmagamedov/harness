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


class ProtoField(ObjectDescription):
    _repeated_prefix = 'repeated '

    def handle_signature(self, sig: str, signode: desc_signature):
        repeated = False
        if sig.startswith(self._repeated_prefix):
            sig = sig[len(self._repeated_prefix):]
            repeated = True
        type_, name = sig.split()
        signode += addnodes.desc_name(name, name)
        if repeated:
            signode += addnodes.desc_annotation('repeated', 'repeated')
        if type_.startswith(('google.', 'harness.')):
            signode += addnodes.pending_xref(
                '',
                addnodes.desc_addname(type_, type_),
                refdomain='proto',
                reftype='message',
                reftarget=type_,
            )
        else:
            signode += addnodes.desc_addname(type_, type_)
        return sig


class ProtoMessage(ObjectDescription):

    def handle_signature(self, sig: str, signode: desc_signature):
        module, name = sig.rsplit('.', 1)
        signode += addnodes.desc_annotation('message', 'message')
        signode += addnodes.desc_addname(module, module + '.')
        signode += addnodes.desc_name(name, name)
        return name

    def add_target_and_index(self, name, sig: str, signode: desc_signature):
        _, targetid = sig.rsplit('.', 1)

        signode['names'].append(targetid)
        signode['ids'].append(targetid)
        self.state.document.note_explicit_target(signode)

        domain = self.env.get_domain('proto')
        assert isinstance(domain, ProtobufDomain), type(domain)
        domain.note_message(self.env.docname, sig, targetid)


class ProtobufDomain(Domain):
    name = 'proto'
    label = 'Protocol Buffers'
    object_types = {
        'message': ObjType(_('message'), 'message'),
    }
    directives = {
        'message': ProtoMessage,
        'field': ProtoField,
    }
    roles = {
        'message': XRefRole(),
    }
    initial_data = {
        'messages': {},
    }

    def note_message(self, docname, target, target_id):
        self.data['messages'][target] = (docname, target_id)

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
        refdoc, target_id = self.data['messages'][target]
        return make_refnode(
            builder,
            fromdocname,
            todocname=refdoc,
            targetid=target_id,
            child=contnode,
            title='',
        )


def setup(app: Sphinx):
    app.add_domain(ProtobufDomain)
