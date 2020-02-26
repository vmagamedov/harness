from typing import List
from dataclasses import dataclass, asdict

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from docutils.parsers.rst import directives


KEY = 'x_bootstrap_wires'


def wire_type(argument):
    return directives.choice(argument, (
        'input',
        'output',
    ))


def wire_runtime(argument):
    return directives.choice(argument, (
        'python',
    ))


@dataclass
class WireInfo:
    value: str
    type: str
    runtime: str
    config: str
    requirements: List[str]


class Wire(SphinxDirective):
    has_content = True
    option_spec = {
        'type': wire_type,
        'runtime': wire_runtime,
        'config': directives.unchanged,
        'requirements': directives.unchanged,
    }

    def run(self):
        missing_options = set(self.option_spec).difference(self.options)
        if missing_options:
            raise ValueError(f'Missing options: {missing_options!r};'
                             f' content: {list(self.content)!r}')
        try:
            wires = getattr(self.env.app, KEY)
        except AttributeError:
            wires = []
            setattr(self.env.app, KEY, wires)
        wires.append(WireInfo(
            value=self.content[0],
            type=self.options['type'],
            runtime=self.options['runtime'],
            config=self.options['config'],
            requirements=self.options['requirements'].split(),
        ))
        return []


def on_html_page_context(app, pagename, templatename, context, doctree):
    if templatename == 'bootstrap.html':
        proto_domain = app.env.get_domain('proto')
        wires_data = []
        for wire in getattr(app, KEY, []):
            wire_data = asdict(wire)
            doc, _ = proto_domain.data['messages'][wire.config]
            wire_data['configProto'] = doc + '.proto'
            wires_data.append(wire_data)
        context[KEY] = wires_data


def setup(app: Sphinx):
    app.add_directive('wire', Wire)
    app.connect('html-page-context', on_html_page_context)
