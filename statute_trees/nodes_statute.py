import json
from pathlib import Path
from typing import Iterator

from pydantic import Field
from statute_patterns import (
    Rule,
    StatuteDetails,
    StatuteTitle,
    StatuteTitleCategory,
)

from .markup import create_tree
from .resources import Node, Page, Tree, TreeishNode, generic_mp
from .utils import has_short_title


class StatuteUnit(Node, TreeishNode):
    """Non-table, interim unit for Statute objects. The `short_title` is used as a special field to look for the statute's title within the provisions."""

    id: str = generic_mp
    short_title: str | None = Field(
        None,
        description="Some unit captions / content signify a title.",
        max_length=500,
    )
    units: list["StatuteUnit"] | None = Field(None)

    @classmethod
    def create_branches(
        cls,
        units: list[dict],
        parent_id: str = "1.",
    ) -> Iterator["StatuteUnit"]:
        for counter, u in enumerate(units, start=1):
            short = None
            children = []  # default unit being evaluated
            id = f"{parent_id}{str(counter)}."
            short = has_short_title(u)
            if subunits := u.pop("units", None):  # potential children
                children = list(cls.create_branches(subunits, id))  # recursive
            yield StatuteUnit(**u, id=id, short_title=short, units=children)

    @classmethod
    def searchables(cls, pk: str, units: list["StatuteUnit"]):
        for u in units:
            if u.caption:
                if u.content:
                    yield dict(
                        material_path=u.id,
                        statute_id=pk,
                        unit_text=f"{u.caption}. {u.content}",
                    )
                else:
                    yield dict(
                        material_path=u.id, statute_id=pk, unit_text=u.caption
                    )
            elif u.content:
                yield dict(
                    material_path=u.id, statute_id=pk, unit_text=u.content
                )
            if u.units:
                yield from cls.searchables(pk, u.units)

    @classmethod
    def finalize_tree(cls, units: list[dict], title: str, kind: str, pk: str):
        branched = list(cls.create_branches(units))
        rooted = cls(id="1.", item=title, units=branched, short_title=None)
        nodes = [rooted.dict(exclude_none=True)]
        return StatuteStructure(
            tree=branched,
            html=create_tree(kind, pk, nodes) if nodes else None,
            units=json.dumps(nodes) if nodes else None,
        )

    @classmethod
    def tree_setup(cls, data: dict, title: str, pk: str):
        if not "units" in data:
            return None
        raw_units = data["units"]
        if not isinstance(raw_units, list):
            return None
        return cls.finalize_tree(raw_units, title, "statute", pk)

    @classmethod
    def granularize(
        cls, pk: str, nodes: list["StatuteUnit"]
    ) -> Iterator[dict]:
        """Recursive flattening of the tree structure so that each material path (with its separate item, caption, and content) can become their own row."""
        for i in nodes:
            data = i.dict()
            data["statute_id"] = pk
            data["material_path"] = data.pop("id")
            yield dict(**data)
            if i.units:
                yield from cls.granularize(pk, i.units)

    @classmethod
    def extract_titles(cls, nodes: list["StatuteUnit"]) -> Iterator[str]:
        for node in nodes:
            if node.short_title:
                yield node.short_title
            if node.units:
                yield from cls.extract_titles(node.units)

    @classmethod
    def get_short(cls, nodes: list["StatuteUnit"]) -> str | None:
        """Get the first short title found."""
        titles = cls.extract_titles(nodes)
        title_list = list(titles)
        if title_list:
            return title_list[0]
        return None


class StatuteStructure(Tree):
    tree: list[StatuteUnit]


class StatutePage(Page):
    titles: list[StatuteTitle]

    @classmethod
    def build(cls, details_path: Path):
        r = Rule.from_path(details_path)
        if not r:
            return "No rule found on path."

        details = StatuteDetails.from_rule(r, details_path.parent)
        if not details:
            return "No details from rule."

        extracted_data = details.dict(exclude={"units"})
        tree_data = StatuteUnit.tree_setup(
            data={"units": details.units},
            title=details.title,
            pk=details.id,
        )
        if not tree_data:
            return "No tree data from details."

        if text := StatuteUnit.get_short(tree_data.tree):
            short = StatuteTitle(
                statute_id=details.id,
                category=StatuteTitleCategory.Short,
                text=text,
            )
            extracted_data["titles"].append(short.dict())
        return cls(**extracted_data, **tree_data.dict(exclude={"tree"}))
