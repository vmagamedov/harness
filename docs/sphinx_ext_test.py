from docutils import nodes
from sphinx.ext import todo
from sphinx.locale import _
from sphinx.application import Sphinx


class test_node(nodes.Admonition, nodes.Element):
    pass


def visit_test_node(self, node):
    self.visit_admonition(node)


def depart_test_node(self, node):
    self.depart_admonition(node)


class Test(todo.Todo):
    node_class = test_node

    def run(self):
        (node,) = super(todo.Todo, self).run()
        node.insert(0, nodes.title(text=_('Test')))
        node['docname'] = self.env.docname
        self.add_name(node)
        self.set_source_info(node)
        self.state.document.note_explicit_target(node)
        return [node]


def setup(app: Sphinx):
    app.add_node(test_node, html=(visit_test_node, depart_test_node))
    app.add_directive('test', Test)
