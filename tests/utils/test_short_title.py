import pytest

from statute_trees.utils._title_unit import has_short_title


@pytest.mark.parametrize(
    "node, checked",
    [
        (
            {
                "item": "Article 1",
                "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)',
            },
            "Civil Code of the Philippines",
        ),
        (
            {
                "item": "Section 1",
                "caption": None,
                "content": "Sample content",
            },
            None,
        ),
    ],
)
def test_has_short_title_content(node, checked):
    assert has_short_title(node) == checked
