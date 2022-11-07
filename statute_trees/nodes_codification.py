import json
from typing import Iterator, Union

from pydantic import Field

from .markup import create_tree
from .resources import (
    CitationAffector,
    Node,
    StatuteAffector,
    Tree,
    TreeishNode,
    generic_mp,
)


class CodeUnit(Node, TreeishNode):
    """For Codification objects. Unlike a Statute which needs to be pre-processed, a Codification is human edited. A Codification is an attempt to unify disconnected Statutes into a single entity. For instance, the `Family Code of the Philippines` is contained in Executive Order No. 209 (1987). However it has since been amended by various laws such as Republic Act No. 8533 (1998) and Republic Act No. 10572 (2013) among others. In light of the need to record a history, each Codification may contain a `history` field."""

    id: str = generic_mp
    history: list[Union[CitationAffector, StatuteAffector]] | None = Field(
        None,
        title="Unit History",
        description="Used in Codifications to show each statute or citation affecting the unit.",
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

    @classmethod
    def finalize_tree(cls, units: list[dict], title: str, kind: str, pk: str):
        branched = list(cls.create_branches(units))
        rooted = cls(id="1.", item=title, units=branched, history=None)
        nodes = [rooted.dict(exclude_none=True)]
        return CodeStructure(
            tree=branched,
            html=create_tree(kind, pk, nodes) if nodes else None,
            units=json.dumps(nodes) if nodes else None,
        )

    @classmethod
    def tree_setup(cls, data: dict, title: str, pk: str):
        if not "units" in data:
            return None
        raw_units = data["units"]
        if not raw_units:
            return None
        if not isinstance(raw_units, list):
            return None
        return cls.finalize_tree(raw_units, title, "codification", pk)


class CodeStructure(Tree):
    tree: list["CodeUnit"] = Field(exclude=True)
