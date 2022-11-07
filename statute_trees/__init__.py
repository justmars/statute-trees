from .markup import create_tree
from .nodes_codification import CodeStructure, CodeUnit
from .nodes_document import DocStructure, DocUnit
from .nodes_statute import StatuteStructure, StatuteUnit
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
