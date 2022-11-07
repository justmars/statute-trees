from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    PackageLoader,
    select_autoescape,
)

from .set_html_tree import TreeConstructor, TreeRouting, TreeStyleCSS

html_templates = Environment(
    loader=FileSystemLoader(Path(__file__).parent),
    autoescape=select_autoescape(),
)


def create_tree(kind: str, pk: str, nodes: list[dict]) -> str:
    """For Codifications, Statutes, and Documents: combines strings which can
    then be read as DOM nodes.

    This will construct a nested DOM node that the resulting tree object can placed in an .html (jinja-powered), specifically in marked with <value_of_the_object_containing_tree>|safe.

    Requirements:
    1. Ensure that the tailwind.config.js file can see the classes declared under `TreeStyleCSS`
    2. Ensure that the .tree class is inserted for the minimal javascript to work
    """
    route = TreeRouting(kind=kind, pk=pk)
    style = TreeStyleCSS(
        container="tree",
        branch="pl-0 sm:pl-3 mt-4 mx-0 mb-0",
        danger="border-l-2 border-rose-600",
        changed="border-l-2 border-indigo-600",
        hovered="text-blue-800 hover:text-rose-600",
        endlink="align-top text-xs text-slate-400",
    )
    obj = TreeConstructor(nodes=nodes, style=style, route=route)
    return obj.tree


def render_tree_on_template(kind: str, pk: str, nodes: list[dict]) -> str:
    tree = create_tree(kind, pk, nodes)
    template = html_templates.get_template("base.html")
    return template.render(tree=tree)


def make_sample_html(kind: str, pk: str, nodes: list[dict]) -> Path:
    templates_folder = Path(__file__).parent / "templates"
    home = templates_folder / "home.html"
    html = render_tree_on_template(kind, pk, nodes)
    home.write_text(html)
    return home
