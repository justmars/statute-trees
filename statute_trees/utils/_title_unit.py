import re

CAPTION_SHORT_TITLE = re.compile(r"short\s*title", re.I)
HAS_TITLE = re.compile(
    "|".join(
        [
            r"""(
            ^
            (This|The)
            \s*
            (Decree|Act|Code)
            \s*
            (may|shall)
            \s*
            be
            \s*
            (cited|known)
        )""",
            r"""(
            ^
            The
            \s*
            short
            \s*
            title
            \s*
            of
            \s*
            this
            \s*
            (Decree|Act|Code)
            \s*
            shall
            \s*
            be
        )""",
        ]
    ),
    re.X | re.I,
)


def extract_quoted_pattern(text: str):
    if match_found := re.compile(r'".*"').search(text):
        return match_found.group().strip('". ')
    elif other_match_found := re.compile(r"“.*”").search(text):
        return other_match_found.group().strip("“”. ")
    return None


def has_short_title(node: dict):
    content = node.get("content")
    if not content:
        return None
    if caption := node.get("caption"):
        if capt_text := caption.strip():
            if CAPTION_SHORT_TITLE.search(capt_text):
                if extract := extract_quoted_pattern(content):
                    return extract
                return content  # not cleaned

    if cont_text := content.strip():
        if matched := HAS_TITLE.search(cont_text):
            if extract := extract_quoted_pattern(cont_text):
                return extract
            return cont_text.replace(matched, "")
    return None
