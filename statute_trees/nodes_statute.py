import json
from collections.abc import Iterator
from pathlib import Path

from pydantic import Field
from statute_patterns import Rule, StatuteTitle

from .resources import Node, Page, StatuteBase, TreeishNode, generic_mp


class StatuteUnit(Node, TreeishNode):
    """Non-table, interim unit for Statute objects. The `short_title` is used as a special field to look for the statute's title within the provisions.
    """

    id: str = generic_mp
    units: list["StatuteUnit"] | None = Field(None)

    @classmethod
    def create_branches(
        cls,
        units: list[dict],
        parent_id: str = "1.",
    ) -> Iterator["StatuteUnit"]:
        for counter, u in enumerate(units, start=1):
            children = []  # default unit being evaluated
            id = f"{parent_id}{str(counter)}."
            if subunits := u.pop("units", None):  # potential children
                children = list(cls.create_branches(subunits, id))  # recursive
            yield StatuteUnit(**u, id=id, units=children)

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
    def granularize(
        cls, pk: str, nodes: list["StatuteUnit"]
    ) -> Iterator[dict]:
        """Recursive flattening of the tree structure so that each material path (with its separate item, caption, and content) can become their own row.
        """
        for i in nodes:
            data = i.dict()
            data["statute_id"] = pk
            data["material_path"] = data.pop("id")
            yield dict(**data)
            if i.units:
                yield from cls.granularize(pk, i.units)


class StatutePage(Page, StatuteBase):
    titles: list[StatuteTitle]
    tree: list[StatuteUnit]

    @classmethod
    def build(cls, details_path: Path):
        """Most of the pre-processing of statute fields is done by `Rules.get_details()`
        """
        details = Rule.get_details(details_path)
        if not details:
            raise Exception("No details from rule.")
        base = StatuteBase.from_rule(details.rule)
        tree = StatuteUnit(
            id="1.",
            item=details.title,
            units=list(StatuteUnit.create_branches(details.units)),
        )
        return cls(
            **details.dict(exclude={"units", "rule"}),
            **base.dict(),
            tree=[tree],
            units=json.dumps([tree.dict(exclude_none=True)]),
        )
