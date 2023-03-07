import json
from collections.abc import Iterator
from pathlib import Path

from pydantic import Field
from statute_patterns import Rule, StatuteTitle, count_rules

from .resources import Node, Page, StatuteBase, TreeishNode, generic_mp


class StatuteUnit(Node, TreeishNode):
    """
    A Statute, as used in this application, is broadly construed. It will refer
    to any Rule imagined by rule-makers (generally legislators) "in the abstract".

    The rule-makers imagine an event that is likely to happen and think of ways
    to deal with such an event.

    For our purposes, a Statute can include the Constitution itself, rules concerning
    pleading, practice, and procedure issued by the Philippine Supreme Court, or even
    the veto message by the President.
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
        """Recursive flattening of the tree structure so that each material path
        (with its separate item, caption, and content) can become their own row.
        """
        for i in nodes:
            data = i.dict()
            data["statute_id"] = pk
            data["material_path"] = data.pop("id")
            yield dict(**data)
            if i.units:
                yield from cls.granularize(pk, i.units)


class MentionedStatute(StatuteBase):
    mentions: int

    @classmethod
    def set_counted_statute(cls, text: str):
        for rule in count_rules(text):
            if mentions := rule.get("mentions"):
                if isinstance(mentions, int) and mentions >= 1:
                    yield cls(
                        statute_category=rule.get("cat"),
                        statute_serial_id=rule.get("id"),
                        mentions=mentions,
                    )


class StatutePage(Page, StatuteBase):
    titles: list[StatuteTitle]
    tree: list[StatuteUnit]

    def join_elements(self, separator: str) -> str | None:
        if not self.variant:
            return None
        if not self.statute_category:
            return None
        if not self.statute_serial_id:
            return None
        if separator not in ("/", "."):
            return None
        if "." in self.statute_serial_id:
            return None
        return separator.join(
            str(i).lower()
            for i in [
                self.statute_category,
                self.date.year,
                self.date.month,
                self.statute_serial_id,
                self.variant,
            ]
        )

    @property
    def storage_prefix(self) -> str | None:
        """Create unique identifier from fields only for use as a
        remote storage prefix. Note parity with `citation_utils.Citation`.
        """
        return self.join_elements(separator="/")

    @property
    def prefix_db_key(self) -> str | None:
        """When identifying the statute in the database, need a way
        to combine fields which can be reverted to storage prefix form
        later. Note parity with `citation_utils.Citation`."""
        return self.join_elements(separator=".")

    @classmethod
    def build(cls, details_path: Path):
        """Most of the pre-processing of statute fields is done by
        `Rules.get_details()` Assuming the .yaml file contains a variant field,
        it will populate the Page variant; otherwise `Rule.get_details` creates
        a default `1`.
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
