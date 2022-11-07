import pytest

from statute_trees.utils import get_node_id


@pytest.fixture
def id_data() -> list[dict]:
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
                            "id": "1.1.1.1",
                        },
                        {
                            "item": "Article 2",
                            "content": "Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)\n",
                            "id": "1.1.1.2",
                        },
                    ],
                    "id": "1.1.1",
                }
            ],
            "id": "1.1",
        }
    ]


def test_get_node_id(id_data):
    assert get_node_id(id_data, "1.1.1.1") == {
        "item": "Article 1",
        "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)\n',
        "id": "1.1.1.1",
    }
