import json
from collections.abc import Iterator
from pathlib import Path
from typing import Union

import yaml
from dateutil.parser import parse
from pydantic import Field
from statute_patterns import StatuteDetails, extract_rule

from .resources import (
    CitationAffector,
    Identifier,
    Node,
    Page,
    StatuteAffector,
    StatuteBase,
    TreeishNode,
    generic_mp,
)


class CodeUnit(Node, TreeishNode):
    """For Codification objects. Unlike a Statute which needs to be pre-processed, a Codification is human edited. A Codification is an attempt to unify disconnected Statutes into a single entity. For instance, the `Family Code of the Philippines` is contained in Executive Order No. 209 (1987). However it has since been amended by various laws such as Republic Act No. 8533 (1998) and Republic Act No. 10572 (2013) among others. In light of the need to record a history, each Codification may contain a `history` field.
    """

    id: str = generic_mp
    history: list[CitationAffector | StatuteAffector] | None = Field(
        None,
        title="Unit History",
        description=(
            "Used in Codifications to show each statute or citation affecting"
            " the unit."
        ),
    )
    units: list["CodeUnit"] | None = Field(None)

    @classmethod
    def create_branches(
        cls, units: list[dict], parent_id: str = "1."
    ) -> Iterator["CodeUnit"]:
        for counter, u in enumerate(units, start=1):
            children = []  # default unit being evaluated
            id = f"{parent_id}{str(counter)}."
            history = u.pop("history", None)
            if subunits := u.pop("units", None):  # potential children
                children = list(cls.create_branches(subunits, id))  # recursive
            yield CodeUnit(
                **u,
                id=id,
                history=history,
                units=children,
            )

    @classmethod
    def searchables(cls, pk: str, units: list["CodeUnit"]):
        for u in units:
            if u.caption:
                if u.content:
                    yield dict(
                        material_path=u.id,
                        codification_id=pk,
                        unit_text=f"{u.caption}. {u.content}",
                    )
                else:
                    yield dict(
                        material_path=u.id,
                        codification_id=pk,
                        unit_text=u.caption,
                    )
            elif u.content:
                yield dict(
                    material_path=u.id, codification_id=pk, unit_text=u.content
                )
            if u.units:
                yield from cls.searchables(pk, u.units)


class CodePage(Page, StatuteBase):
    tree: list[CodeUnit]

    @classmethod
    def build(cls, file_path: Path):
        data = yaml.safe_load(file_path.read_text())
        title = data.get("title")
        emails = data.get("emails", ["bot@lawsql.com"])
        variant = data.get("variant", 1)
        date = parse(data.get("date")).date()
        rule = extract_rule(data.get("base"))
        if not rule:
            return None
        tree = CodeUnit(
            id="1.",
            item=title,
            units=list(CodeUnit.create_branches(data.get("units"))),
            history=None,
        )
        return cls(
            created=file_path.stat().st_ctime,
            modified=file_path.stat().st_mtime,
            id=Identifier(
                text="-".join([rule.cat, rule.id, title]),
                date=date,
                variant=variant,
                emails=emails,
            ).slug,
            emails=emails,
            title=title,
            description=data.get("description"),
            date=date,
            variant=variant,
            tree=[tree],
            units=json.dumps([tree.dict(exclude_none=True)]),
            **StatuteBase.from_rule(rule).dict(),
        )
