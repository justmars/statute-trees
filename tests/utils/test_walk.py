import pytest

from statute_trees.utils import fetch_values_from_key


@pytest.fixture
def raw_data() -> list[dict]:
    return [
        {
            "item": "Preliminary Title",
            "units": [
                {
                    "item": "Chapter 1",
                    "caption": "Effect and Application of Laws",
                    "units": [
                        {
                            "item": "Article 1",
                            "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)\n',
                        },
                        {
                            "item": "Article 2",
                            "content": "Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)\n",
                        },
                    ],
                }
            ],
        }
    ]


def test_fetch_values_from_key(raw_data):
    node_data: dict = raw_data[0]
    values = fetch_values_from_key(node_data, "item")
    assert list(values) == [
        "Preliminary Title",
        "Chapter 1",
        "Article 2",
        "Article 1",
    ]


def test_cant_fetch_values_from_list(raw_data):
    fetch_values_from_key(raw_data, "item")
    assert AttributeError
