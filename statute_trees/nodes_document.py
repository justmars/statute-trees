import json
from typing import Iterator, Union

from pydantic import Field

from .markup import create_tree
from .resources import (
    EventCitation,
    EventStatute,
    FTSQuery,
    Node,
    Tree,
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

    @classmethod
    def finalize_tree(cls, units: list[dict], title: str, kind: str, pk: str):
        branched = list(cls.create_branches(units))
        rooted = cls(id="1.", item=title, units=branched, sources=None)
        nodes = [rooted.dict(exclude_none=True)]
        return DocStructure(
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
        return cls.finalize_tree(raw_units, title, "document", pk)


class DocStructure(Tree):
    tree: list["DocUnit"] = Field(exclude=True)
