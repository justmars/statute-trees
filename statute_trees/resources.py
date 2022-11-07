import datetime
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterator

from citation_utils import Citation
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    Json,
    root_validator,
    validator,
)
from slugify import slugify
from statute_patterns import Rule, StatuteSerialCategory, extract_rule

"""
Note: The fields are marked with col and index for future use by the sqlpyd library.
"""

generic_mp = Field(
    ...,
    title="Material Path ID",
    description="The material path of the unit within the document. All tree-like documents should start with 1.; all children of 1. will use this as a prefix, e.g. 1.1., 1.2., etc.",
    regex=r"^(\d+\.)+$",
    col=str,
    index=True,
)
generic_item = Field(
    ...,
    title="Item or Locator",
    description="Primarily determines positioning of the unit sought within a tree; e.g Section 1, Container 1, etc.",
    col=str,
    index=True,
)
generic_caption = Field(
    None,
    title="Caption",
    description="When supplied, this provides additional context of the unit sought within a tree.",
    max_length=5000,
    col=str,
    index=True,
    fts=True,
)
generic_content = Field(
    None,
    title="Content",
    description="When supplied, this provides the content proper of the unit sought within a tree.",
    max_length=100000,
    col=str,
    index=True,
    fts=True,
)
generic_variant = Field(
    1,
    title="Document / Statute / Codification Variant",
    description="If not supplied, the variant should be 1. There are statutes which have the same category, id, and date, requiring a third-party key to make the value unique. This is the variant key. Example: Administrative Matter No. 19-03-24-SC.",
    col=int,
    index=True,
)
generic_title = Field(
    title="Page Title",
    description="Should be limited in length for HTML.",
    max_length=500,
    col=str,
    index=True,
    fts=True,
)
generic_description = Field(
    title="Page Description",
    description="Should be limited in length for HTML.",
    max_length=5000,
    col=str,
    index=True,
    fts=True,
)
generic_email = Field(
    ["bot@lawsql.com"],
    title="Author / Formatter",
    description="Every tree object can be attributable to its maker.",
)


SECTION = re.compile(
    r"""
    ^\s*
    S
    (
        ECTION|
        EC|
        ec
    )
    [\s.,]+
""",
    re.X,
)


def normalize_sec(item: str):
    v = str(item).strip()
    if v and SECTION.search(v):
        return SECTION.sub("Section ", v).strip("., ")
    return v


def normalize_caption(caption: str | None):
    if caption:
        return str(caption)
    return None


class Identifier(BaseModel):
    """Create a unique identifier `slug` based on common fields."""

    text: str
    date: datetime.date
    variant: int = generic_variant
    emails: list[EmailStr] = generic_email

    @property
    def slug(self):
        """Extracts the first name of the email address, adds the year from the date and joins the details to forms a single slug."""
        authors = "-".join(email.split("@")[0] for email in self.emails)
        elements = [authors, self.date.year, self.text, f"v{self.variant}"]
        joined_text = "-".join((str(e) for e in elements))
        slug = slugify(joined_text)
        return slug


class Tree(BaseModel):
    html: str | None = Field(
        None,
        description="The DOM string of the tree based on the units field (as formatted by the markup library).",
        col=str,
    )
    units: str | None = Field(
        None,
        title="Unit Tree.",
        description="Tree in JSON string format that can be formatted via html.",
        col=str,
    )


class Page(Tree):
    """HTML pages will require a `title` and a `description`. Contains the following common fields for use in tree-like structures: `created`, `modified`, `id`, `variant`, `units`."""

    created: float = Field(col=float)
    modified: float = Field(col=float)
    id: str = Field(
        ...,
        title="Non-traditional identifier created by slugifying certain fields.",
        description="Primary key.",
        col=str,
    )
    title: str = generic_title
    description: str = generic_description
    date: datetime.date = Field(
        ...,
        col=datetime.date,
        index=True,
    )
    variant: int = generic_variant


class Node(BaseModel):
    """Generic node containing the `item`, `caption` and `content` fields. Used in all tree-like structures to signify a node in the tree."""

    item: str = generic_item
    caption: str | None = generic_caption
    content: str | None = generic_content

    # validators
    _sectionize_item = validator("item", allow_reuse=True)(normalize_sec)
    _string_cap = validator("caption", allow_reuse=True)(normalize_caption)

    class Config:
        anystr_strip_whitespace = True


class StatuteBase(BaseModel):
    """Unlike a `Rule` object under `statute_patterns`, the fields for category and serial id are optional since a passed statute may not have been included in the limited set of statutes included in the `extract_rules()` function."""

    statute_category: StatuteSerialCategory | None = Field(
        None, col=str, index=True
    )
    statute_serial_id: str | None = Field(None, col=str, index=True)

    @validator("statute_category", pre=True)
    def category_in_lower_case(cls, v):
        return StatuteSerialCategory(v.lower()) if v else None

    @validator("statute_serial_id", pre=True)
    def serial_id_lower(cls, v):
        return v.lower() if v else None

    @classmethod
    def from_rule(cls, r: Rule):
        return cls(statute_category=r.cat, statute_serial_id=r.id)


class EventStatute(StatuteBase):
    """The statute + unit item affecting a Codification unit. The combination of the `statute_category`, `statute_serial_id`, `date` and `variant` make it possible to get unique Statute documents."""

    locator: str = generic_item
    caption: str | None = generic_caption
    content: str | None = generic_content
    statute: str = Field(
        ...,
        title="Serial Statute Title",
        description="Text that is parseable, see statute-patterns; will generate a `statute_category` and `statute_serial_id`. e.g. 'Republic Act No. 386' produces `ra` and `386`, respectively.",
        min_length=4,
        col=str,
        index=True,
    )
    variant: int = generic_variant
    date: datetime.date = Field(None, col=datetime.date)

    # validators
    _sectionize_loc = validator("locator", allow_reuse=True)(normalize_sec)
    _string_cap = validator("caption", allow_reuse=True)(normalize_caption)

    @root_validator(pre=True)
    def split_statute(cls, values):
        if stat := values.get("statute"):
            if rule := extract_rule(stat):
                values["statute_category"] = rule.cat
                values["statute_serial_id"] = rule.id
        return values

    @validator("date", pre=True)
    def date_in_isoformat(cls, v):
        if not v:
            return None
        try:
            if isinstance(v, str):
                return parse(v).date()
        except Exception as e:
            return ValueError(f"Bad date {v=}; {e=}")
        return v

    class Config:
        anystr_strip_whitespace = True


class StatuteAffectorAction(str, Enum):
    """The effect of the statutory item on a Codification unit.."""

    Originated = "Originated"
    Amended = "Amended"
    Modified = "Modified"
    Adopted = "Adopted"
    Inserted = "Inserted"
    Renumbered = "Renumbered"
    Deleted = "Deleted"
    Repealed = "Repealed"
    Interpreted = "Interpreted"
    Associated = "Associated"
    Vetoed = "Vetoed"


class StatuteAffector(EventStatute):
    action: StatuteAffectorAction = Field(
        StatuteAffectorAction.Originated,
        title="Codification Event Action",
        description="The action of the event in relation to a Codification provision,",
        col=str,
    )

    class Config:
        use_enum_values = True


class FTSQuery(BaseModel):
    """Full text search query for sqlite3."""

    query: str = Field(
        ...,
        title="FTS5 SQLite-Based Expression",
        description='e.g. "power to tax" AND ("sovereignty" OR "lifeblood" OR "security against its abuse" OR "responsibility of the legislature")',
        min_length=5,
        col=str,
    )

    @validator("query")
    def query_is_lineless(cls, v):
        return re.sub(r"\s*\n", "", v).strip()


class CitationAffectorAction(str, Enum):
    """The effect of the citation item on a Codification unit."""

    Unconstitutional = "Unconstitutional"
    Interpreted = "Interpreted"


class EventCitation(BaseModel):
    """The citation item affecting a Codification unit."""

    citation: str = Field(
        ...,
        title="Text that is parseable via citation-utils",
        description="e.g. '1 SCRA 1' or 'GR No. 12414, Dec. 14, 2000'",
        min_length=6,
        col=str,
    )

    @validator("citation")
    def citation_must_be_uniform(cls, v):
        if docs := list(Citation.find_citations(v)):
            if len(docs) == 1:
                doc = docs[0]
                return doc.docket or doc.scra or doc.phil or doc.offg
            return ValueError(f"Too many citations found {docs=}")
        return ValueError(f"No citations found {v=}")


class CitationAffector(EventCitation):
    """Events can be sourced from a decision. The `decision_title` is represented by the `citation`. The event's effect is signified through the `action` as contextualized through supplied context in the `snippet`.."""

    decision_title: str = Field(
        ...,
        title="Decision Title",
        description="Text can represent the decision as a short title, e.g. 'Tañada v. Tuvera'",
        min_length=6,
        max_length=100,
        col=str,
        index=True,
    )
    snippet: str = Field(
        ...,
        title="Snippet of the Decision",
        description="Text of the decision that is relevant in describing the context of the action.",
        min_length=6,
        col=str,
        index=True,
        fts=True,
    )
    action: CitationAffectorAction = Field(
        CitationAffectorAction.Interpreted,
        col=str,
        index=True,
    )

    class Config:
        use_enum_values = True
        anystr_strip_whitespace = True


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
