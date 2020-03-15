from enum import Enum
from typing import List
from collections import defaultdict
from dataclasses import dataclass

from docutils import nodes
from pkg_resources import parse_version
from sphinx.application import Sphinx
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

import harness


CURRENT_VERSION = parse_version(harness.__version__)


class ChangeType(Enum):
    BUG = "bug"
    FEATURE = "feature"
    SUPPORT = "support"


_COLORS = {
    ChangeType.BUG: "#A04040",
    ChangeType.FEATURE: "#40A056",
    ChangeType.SUPPORT: "#4070A0",
}


@dataclass
class ChangeEntry:
    type: ChangeType
    since: List[str]
    content: str


class Changelog(SphinxDirective):
    has_content = True

    def run(self):
        self.env.temp_data["x-changes"] = []
        self.state.nested_parse(self.content, 0, nodes.paragraph("", ""))

        by_base_version = defaultdict(list)
        for change in self.env.temp_data["x-changes"]:
            for version in change.since:
                p_version = parse_version(version)
                if p_version <= CURRENT_VERSION:
                    base_version = parse_version(p_version.base_version)
                    by_base_version[base_version].append(change)

        version_sections = []
        for base_version in sorted(by_base_version, reverse=True):
            ident = f"v{base_version}"
            if CURRENT_VERSION.is_prerelease and CURRENT_VERSION.base_version == str(
                base_version
            ):
                title = f"v{base_version} (dev)"
            else:
                title = f"v{base_version}"
            version_section = nodes.section("", nodes.title(title, title), ids=[ident])
            changes_list = nodes.bullet_list("")
            for change in by_base_version[base_version]:
                change_p = nodes.paragraph("", "")
                self.state.nested_parse(change.content, 0, change_p)
                change_p[0].insert(0, nodes.inline(text=": "))
                change_p[0].insert(
                    0,
                    nodes.raw(
                        text='[<span style="color: {};">{}</span>]'.format(
                            _COLORS[change.type], change.type.name.capitalize(),
                        ),
                        format="html",
                    ),
                )
                changes_list += nodes.list_item("", *change_p)
            version_section += changes_list
            version_sections.append(version_section)
        return version_sections


class Change(SphinxDirective):
    has_content = True
    option_spec = {
        "type": lambda arg: directives.choice(
            arg, [e.value for e in ChangeType.__members__.values()],
        ),
        "since": directives.unchanged_required,
    }

    def run(self):
        self.env.temp_data["x-changes"].append(
            ChangeEntry(
                type=ChangeType(self.options["type"]),
                since=self.options["since"].split(),
                content=self.content,
            )
        )
        return []


def setup(app: Sphinx):
    app.add_directive("changelog", Changelog)
    app.add_directive("change", Change)
