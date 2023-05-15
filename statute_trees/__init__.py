__version__ = "0.1.5"

from .nodes_codification import CodePage, CodeUnit
from .nodes_document import DocPage, DocUnit
from .nodes_statute import MentionedStatute, StatutePage, StatuteUnit
from .resources import (
    CitationAffector,
    EventCitation,
    EventStatute,
    Identifier,
    Node,
    Page,
    StatuteAffector,
    StatuteBase,
    generic_content,
    generic_email,
    generic_mp,
    generic_variant,
)
from .utils import set_node_ids
