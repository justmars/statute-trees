import pytest

from statute_trees.utils import Layers


@pytest.fixture
def itemless_data() -> list[dict]:
    return [
        {
            "item": "Part I",  # should be ignored; second level should start with I.
            "units": [
                {
                    "caption": "Effect and Application of Laws",
                    "units": [
                        {
                            "content": (
                                'This Act shall be known as the "Civil Code of'
                                ' the Philippines." (n)\n'
                            ),
                            "units": [
                                {
                                    "caption": "Sample",
                                    "units": [
                                        {"caption": "Even more samples"},
                                        {"caption": "Hello world!"},
                                        {"caption": "Lowest level!"},
                                    ],
                                },
                            ],
                        },
                        {
                            "content": (
                                "Laws shall take effect after fifteen days"
                                " following the completion of their"
                                " publication either in the Official Gazette"
                                " or in a newspaper of general circulation in"
                                " the Philippines, unless it is otherwise"
                                " provided. (1a)\n"
                            ),
                        },
                    ],
                }
            ],
        }
    ]


def test_layered_items(itemless_data):
    Layers.DEFAULT.layerize(itemless_data)
    assert itemless_data == [
        {
            "item": "Part I",
            "units": [
                {
                    "caption": "Effect and Application of Laws",
                    "units": [
                        {
                            "content": (
                                'This Act shall be known as the "Civil Code of'
                                ' the Philippines." (n)\n'
                            ),
                            "units": [
                                {
                                    "caption": "Sample",
                                    "units": [
                                        {
                                            "caption": "Even more samples",
                                            "item": "§a",
                                        },
                                        {
                                            "caption": "Hello world!",
                                            "item": "§b",
                                        },
                                        {
                                            "caption": "Lowest level!",
                                            "item": "§c",
                                        },
                                    ],
                                    "item": "§1",
                                }
                            ],
                            "item": "§A",
                        },
                        {
                            "content": (
                                "Laws shall take effect after fifteen days"
                                " following the completion of their"
                                " publication either in the Official Gazette"
                                " or in a newspaper of general circulation in"
                                " the Philippines, unless it is otherwise"
                                " provided. (1a)\n"
                            ),
                            "item": "§B",
                        },
                    ],
                    "item": "§I",
                }
            ],
        }
    ]
