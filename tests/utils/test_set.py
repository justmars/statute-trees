import pytest

from statute_trees.utils import set_node_ids


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


def test_set_node_ids(raw_data):
    set_node_ids(raw_data)  # will modify the data in place
    assert raw_data == [
        {
            "id": "1.1.",
            "item": "Preliminary Title",
            "units": [
                {
                    "id": "1.1.1.",
                    "item": "Chapter 1",
                    "caption": "Effect and Application of Laws",
                    "units": [
                        {
                            "id": "1.1.1.1.",
                            "item": "Article 1",
                            "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)\n',
                        },
                        {
                            "id": "1.1.1.2.",
                            "item": "Article 2",
                            "content": "Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)\n",
                        },
                    ],
                }
            ],
        }
    ]
