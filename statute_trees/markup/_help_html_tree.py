import re
from typing import Match


def is_text_containerish_collapsible(candidate) -> bool:
    return isinstance(candidate, str) and (
        candidate.startswith("§")
        or candidate.startswith("Section")
        or candidate.startswith("Article")
        or candidate.startswith("Container")
        or candidate.startswith("Sub-Container")
        or candidate.startswith("Part")
        or candidate.startswith("Subsection")
        or candidate.startswith("Rule")
        or candidate.startswith("Book")
        or candidate.startswith("Chapter")
        or candidate.startswith("Title")
        or candidate.endswith("Provision")
        or candidate.endswith("Provisions")
        or "Preliminary Title" in candidate
        or "Preliminary Chapter" in candidate
        or "Repealing Clause" in candidate
    )


def should_hide(text: str) -> bool | Match[str] | None:
    generic_clause_pattern = re.compile(
        r"(First|Second|Third|Fourth|Fifth|Whereas|Enacting)\sClause"
    )
    return isinstance(text, str) and (
        text.startswith("Paragraph")
        or text.startswith("Sub-Paragraph")
        or text.startswith("Container")
        or text.startswith("Sub-Container")
        or text.startswith("Proviso")
        or text.startswith("Sub-Proviso")
        or text.startswith("Clause")
        or generic_clause_pattern.search(text)
    )


def ensure_dot(text: str):
    """Ensures that a period is added to the text, in case it doesn't have
    one."""
    if isinstance(text, str) and text.endswith("."):
        return text
    return f"{text}."


def merge_at_start(headline: str | None, content: str):
    try:
        target = "<p>"
        idx = content.index(target)  # position of <p> in content
    except Exception as e:
        return f"{headline} {content}"
    if headline:
        try:
            balance = content[idx + len(target) :]
            result = target + headline + " " + balance
            return result
        except Exception as e:
            ...
    return content


def merge_at_end(url: str, content: str | None = None):
    if not content:
        return None
    if "</p>" in content:
        target = "</p>"
        idx = content.rindex(target)  # position of </p> in content
        start = content[:idx]
        result = start + url + target
        return result
    return content + url


def use_summary(
    item: str | None = None,
    content: str | None = None,
    children: list[dict] | None = None,
) -> bool:
    if item and is_text_containerish_collapsible(item) and not content:
        # initial matches criteria
        if children and not is_first_child_a_paragraph_item(children):
            # second check matches special cases: if the first child is a paragraph, then do not use <details><summary> tags
            return True
    return False


def should_add_endlink(item, content) -> bool:
    """For parts of the tree that need links but without obvious items to link
    to, mark as true for further processing."""
    if (
        item
        and isinstance(item, str)
        and (item.startswith("Paragraph") or item.startswith("Proviso"))
        and content
    ):
        return True
    return False


def extract_child_paragraph(
    children: list[dict] | None,
) -> tuple[str | None, list[dict]]:
    """Without this, the first child paragraph would be indented in a separate
    line.

    Instead of creating a separate line, extract the first item from the
    children.
    """
    if not children:
        return None, []
    if is_first_child_a_paragraph_item(children):
        if children[0].get("content", None):
            child = children.pop(0)
            return (child["content"], children)
    return None, children


def is_paragraph_next(target: str) -> bool:
    return (
        True
        if target
        and isinstance(target, str)
        and target.startswith("Paragraph")
        and not target.strip().endswith("1")
        else False
    )


def is_first_child_a_paragraph_item(children) -> bool:
    return (
        children
        and "item" in children[0]
        and isinstance(children[0]["item"], str)
        and children[0]["item"].startswith("Paragraph")
        and children[0]["item"].endswith("1")
    )
