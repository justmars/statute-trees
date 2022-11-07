from dataclasses import dataclass
from typing import Iterator, NamedTuple

from markdown import markdown

from ._help_html_tree import (
    ensure_dot,
    extract_child_paragraph,
    merge_at_end,
    merge_at_start,
    should_add_endlink,
    should_hide,
    use_summary,
)


class TreeStyleCSS(NamedTuple):
    container: str
    branch: str
    danger: str
    changed: str
    hovered: str
    endlink: str

    @property
    def danger_branch(self):
        return f"{self.branch} {self.danger}"

    @property
    def changed_branch(self):
        return f"{self.branch} {self.changed}"


class TreeRouting(NamedTuple):
    """Helps build the proper route to materialized unit paths with a setter function"""

    kind: str
    pk: str

    def setter(self, material_path: str):
        texts = [self.kind, self.pk, "unit", material_path]
        route = "/".join(texts)
        return f"/{route}"


@dataclass
class TreeConstructor:
    """Using `nodes` (markdown), construct a dynamic (marked-up html) tree, with css `style`s, based on URL `route`s."""

    nodes: list[dict]  # the full list of nodes
    style: TreeStyleCSS  # the manner of styling nodes based on properties
    route: TreeRouting  # each material path will have its own dynamic url location

    def __post_init__(self):
        branches = self.add_branch(self.nodes)
        self.tree = self.set_tree(branches)

    def set_tree(self, branches: Iterator[str]) -> str:
        """Combines strings which can then be read as DOM nodes."""
        open_tag = f"<article class='{self.style.container}'>"
        close_tag = "</article>"
        dom_nodes = [open_tag] + list(branches) + [close_tag]
        partial_html = "".join(dom_nodes)
        return partial_html

    def add_branch(self, nodes: list[dict]) -> Iterator[str]:
        """Accepts a nested list of markdown-formatted nodes to produce a formatted
        iterator of html structures that can later be joined.

        Each node must consist of item, caption, content or a variation of
        the same.
        """
        # open <ul> tag
        yield f"<ul class='{self.style.branch}'>"

        # for each node, open an <li> tag corresponding to the parent <ul>
        for node in nodes:
            # each node may contain certain keys
            idx, item, caption, content, children, history_list = (
                node.get("id", None),
                node.get("item", " "),  # make this a blank space
                node.get("caption", None),
                node.get("content", None),
                node.get("units", None),
                node.get("history", None),
            )

            content = (
                markdown(content.strip(), extensions=["tables"])
                if content
                else None
            )
            if not idx:
                raise Exception(f"Missing id in {node=}")
            route = self.route.setter(idx)

            # clicking on headline link leads to sub portion of the tree based on the idx
            headline = self.add_link_label(route, item, caption)

            # although no headline, can still create link via right caret `&#8594;` to individual Paragraphs / Provisos as children units
            if should_add_endlink(item, content):
                caret = self.add_url(
                    url=route, text=">", tooltip_text=item, endline=True
                )
                content = merge_at_end(caret, content)

            # open <li> tag, possibly changing color / tooltip of node
            yield self.open_li_tag(item, history_list)

            # determine tag to use; relevant for creating summarizable headlines
            if summarizable := use_summary(item, content, children):
                yield f"<details><summary>{headline}</summary>"

            else:
                # since not summarizable, start formatting content
                if content:
                    yield merge_at_start(headline, content)
                else:
                    # with first paragraph extracted, implies that this should be merged with the headline
                    extract, children = extract_child_paragraph(children)
                    if extract:
                        # note the 1. in the url (vs. add_url above), since the first paragraph has been extracted, there's a different ID for it
                        caret = self.add_url(
                            url=f"{route}1.",
                            text=">",
                            tooltip_text="Paragraph 1",
                            endline=True,
                        )
                        if modified_par := merge_at_end(caret, extract):
                            yield merge_at_start(headline, modified_par)
                    else:  # no content found so just not summarizable headline
                        if headline:
                            yield headline

            # if the node contains a 'units' key, extract the nodes
            if children:
                yield from self.add_branch(children)

            # close if it was opened earlier
            if summarizable:
                yield "</details>"

            # close li tag
            yield "</li>"

        # close tag
        yield "</ul>"

    def open_li_tag(
        self, target: str, history_list: list[dict] | None = None
    ) -> str:
        if history_list:
            node = history_list[-1]
            if action := node.get("action", None):
                act = action.lower()
                locator, statute, citation, decision = (
                    node.get("locator", None),
                    node.get("statute", None),
                    node.get("citation", None),
                    node.get("decision", None),
                )
                if act in ["unconstitutional"]:
                    text = f"{target} {act} by {decision}, {citation}"
                    return f"<li class='{self.style.danger_branch}' title='{text}' data-tooltip='{text}'>"
                elif act in ["repealed", "deleted"]:
                    text = f"{target} {act} by {statute}, {locator}"
                    return f"<li class='{self.style.danger_branch}' title='{text}' data-tooltip='{text}'>"
                elif act in ["modified"]:
                    text = f"{target} {act} by {statute}, {locator}"
                    return f"<li class='{self.style.changed_branch}' title='{text}' data-tooltip='{text}'>"
        return f"<li class='{self.style.branch}'>"

    def add_url(
        self, url: str, text: str, tooltip_text: str, endline: bool = False
    ) -> str:
        tooltip = f"Focus on {tooltip_text}"
        attributes = f"class='{self.style.hovered}' href='{url}' title='{tooltip}' data-tooltip='{tooltip}'"
        if endline:
            return f"<a class='{self.style.endlink} {self.style.hovered}' {attributes}>{text}</a>"
        return f"<a {attributes}>{text}</a>"

    def add_link_label(
        self,
        url: str,
        item: str | None = None,
        caption: str | None = None,
    ):
        if item or caption:
            if item and should_hide(item):
                if caption:
                    return self.add_url(
                        url,
                        f"<em>{caption}.</em>",
                        caption,
                    )
                else:
                    return self.add_url(
                        url, f"<span style='display:none'>{item}</span>", item
                    )
            elif item and item == "":
                #  Hide
                return self.add_url(
                    url, f"<span style='display:none'>{item}</span>", item
                )
            else:
                if item and caption:
                    return self.add_url(
                        url,
                        f"{ensure_dot(item)} <em>{caption}</em>",
                        f"{ensure_dot(item)} {caption}",
                    )
                elif item:
                    return self.add_url(url, ensure_dot(item), item)
                elif caption:
                    return self.add_url(
                        url, f"<em>{ensure_dot(caption)}</em>", caption
                    )
