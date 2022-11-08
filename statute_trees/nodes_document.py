import json
from pathlib import Path
from typing import Iterator, Union

import yaml
from dateutil.parser import parse
from pydantic import Field

from .resources import (
    EventCitation,
    EventStatute,
    FTSQuery,
    Identifier,
    Node,
    Page,
    TreeishNode,
    generic_mp,
)
from .utils import Layers


class DocUnit(Node, TreeishNode):
    """Non-table, interim unit for Document objects."""

    id: str = generic_mp
    sources: list[Union[EventStatute, EventCitation, FTSQuery]] | None = Field(
        None,
        title="Legal Basis Sources",
        description="Used in Documents to show the basis of the content node.",
    )
    units: list["DocUnit"] = Field(None)

    @classmethod
    def create_branches(
        cls, units: list[dict], parent_id: str = "1."
    ) -> Iterator["DocUnit"]:
        if parent_id == "1.":
            Layers.DEFAULT.layerize(units)  # in place
        for counter, u in enumerate(units, start=1):
            children = []  # default unit being evaluated
            id = f"{parent_id}{str(counter)}."
            sources = u.pop("sources", None)
            if subunits := u.pop("units", None):  # potential children
                children = list(cls.create_branches(subunits, id))  # recursive
            yield DocUnit(**u, id=id, sources=sources, units=children)

    @classmethod
    def searchables(cls, pk: str, units: list["DocUnit"]):
        for u in units:
            if u.caption:
                if u.content:
                    yield dict(
                        material_path=u.id,
                        document_id=pk,
                        unit_text=f"{u.caption}. {u.content}",
                    )
                else:
                    yield dict(
                        material_path=u.id,
                        document_id=pk,
                        unit_text=u.caption,
                    )
            elif u.content:
                yield dict(
                    material_path=u.id,
                    document_id=pk,
                    unit_text=u.content,
                )
            if u.units:
                yield from cls.searchables(pk, u.units)


class DocStructure(Page):
    tree: list[DocUnit]

    @classmethod
    def build(cls, file_path: Path):
        data = yaml.safe_load(file_path.read_text())
        title = data.get("title")
        emails = data.get("emails", ["bot@lawsql.com"])
        variant = data.get("variant", 1)
        date = parse(data.get("date")).date()
        tree = DocUnit(
            id="1.",
            item=title,
            units=list(DocUnit.create_branches(data.get("units"))),
            sources=None,
        )
        return cls(
            created=file_path.stat().st_ctime,
            modified=file_path.stat().st_mtime,
            id=Identifier(
                text=data["title"],
                date=parse(data.get("date")).date(),
                variant=data.get("variant", 1),
                emails=data.get("emails", ["bot@lawsql.com"]),
            ).slug,
            emails=emails,
            title=title,
            description=data.get("description"),
            date=date,
            variant=variant,
            tree=[tree],
            units=json.dumps([tree.dict(exclude_none=True)]),
        )
