import json
from abc import ABC, abstractmethod
from typing import Iterator, Union

from pydantic import Field

from .markup import create_tree
from .resources import (
    CitationAffector,
    EventCitation,
    EventStatute,
    FTSQuery,
    Node,
    StatuteAffector,
    Tree,
    generic_mp,
)
from .utils import Layers, has_short_title


class TreeishNode(ABC):
    """The building block of the tree. Each category of tree is different since the way they're built is nuanced, e.g. CodeUnits need a `history` field, and DocUnits need a `sources` field. However both types share the same foundational structure."""

    @classmethod
    @abstractmethod
    def create_branches(cls, units: list[dict], parent_id: str = "1."):
        """Each material path tree begins will eventually start with a root of `1.` so that each branch will be a material path (identified by the `id`) to the root."""
        raise NotImplementedError(
            "Tree-based nodes must have a create_branches() function; note that each branching function for each tree category is different."
        )

    @classmethod
    @abstractmethod
    def searchables(cls, pk: str, units: list) -> Iterator[dict]:
        """The `pk` indicated refers to the container, i.e. the foreign key Codification / Statute / Document. So every dict generated will have a unique material path with a `unit_text` that is searchable and highlightable via sqlite's FTS."""
        raise NotImplementedError(
            "Tree-based nodes must generate sqlite-compatible fts unit_text columns that is searchable and whose snippet (see sqlite's snippet() function) can be highlighted."
        )

    @classmethod
    @abstractmethod
    def finalize_tree(
        cls, units: list[dict], title: str, kind: str, pk: str
    ) -> dict:
        """Generate a valid json string that is queryable via sqlite JSON1 and an html string built from tailwind classes, see `.markup.create_tree()`"""
        raise NotImplementedError(
            "Tree-based nodes must result in a valid json string for sqlite and a valid html string to display as jinja variable."
        )

    @classmethod
    @abstractmethod
    def tree_setup(cls, data: dict, title: str, pk: str):
        """Given a dictionary with a key `units`, create a tree whose root will have a `title` and whose subnodes, branches will have a url having a uniform prefix, signifying that the node belongs to an object with said `pk`."""
        raise NotImplementedError(
            "Wrapper around finalize_tree based on a dictionary `data` with a key `units`."
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
            yield DocUnit(
                **u,
                id=id,
                sources=sources,
                units=children,
            )

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
    def get_first_title(cls, nodes: list["StatuteUnit"]) -> str | None:
        titles = cls.extract_titles(nodes)
        title_list = list(titles)
        if title_list:
            return title_list[0]
        return None


class CodeStructure(Tree):
    tree: list["CodeUnit"] = Field(exclude=True)


class StatuteStructure(Tree):
    tree: list["StatuteUnit"] = Field(exclude=True)


class DocStructure(Tree):
    tree: list["DocUnit"] = Field(exclude=True)
