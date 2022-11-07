import string
from enum import Enum
from typing import Iterator, NamedTuple

DIGIT_RANGE = range(1, 79)
"""This enables an enumeration of 1 to 78, that's three iterations of the alphabet, 26 * 3"""


def romanize(num: int) -> str:
    m = ["", "M", "MM", "MMM"]
    c = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM "]
    x = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
    i = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
    thousands = m[num // 1000]
    hundreds = c[(num % 1000) // 100]
    tens = x[(num % 100) // 10]
    ones = i[num % 10]
    return thousands + hundreds + tens + ones


def multi_alpha(collection: str, multiplier: int = 1) -> Iterator[str]:
    """If the collection is abcde, and the multiplier is 2, then each item
    yielded will be of the following form: 'aa', 'bb', 'cc', etc."""
    for ch in collection:
        yield f"{ch*multiplier}"


def set_alphabet(collection: str, max: int = 3):
    """Auto-generate repeating letters based on the increasing range; so if the
    max is 3, the range created is 1 to 4.

    Each item in the range will become a multiplier to each character of
    the `collection` sequence.
    """
    for i in range(1, max + 1):
        yield from multi_alpha(collection, i)


class ListType(Enum):
    DIGITS = [i for i in DIGIT_RANGE]
    UPPER_ALPHA = list(set_alphabet(string.ascii_uppercase, 3))
    LOWER_ALPHA = list(set_alphabet(string.ascii_lowercase, 3))
    UPPER_ROMAN = [romanize(i) for i in DIGIT_RANGE]
    LOWER_ROMAN = [romanize(i).lower() for i in DIGIT_RANGE]


class Layers(Enum):
    """Different tree types may have different layering enumerations.

    For the default case, we'll use a standard way of nesting legal documents:
    I. (Upper Roman from I to LXXVIII)
        A. (Upper Alpha from A to ZZZ)
            1. (General Digits from 1 to 78)
                a. (Lower Alpha from a to zzz)
                    i. (Lower Roman from i to lxxviii)

    There can be other formats added later.
    """

    DEFAULT = (
        ListType.UPPER_ROMAN,
        ListType.UPPER_ALPHA,
        ListType.DIGITS,
        ListType.LOWER_ALPHA,
        ListType.LOWER_ROMAN,
        ListType.DIGITS,  # repeats starting with digits and lower cased enumerations
        ListType.LOWER_ALPHA,
        ListType.LOWER_ROMAN,
    )

    def get_item_type(self, level: int) -> ListType:
        max_layer_count = len(self.value)
        if not 0 < level <= max_layer_count:
            raise Exception(f"{max_layer_count=} {self.name}; bad {level=}.")
        return self.value[level - 1]  # lowest level is 1: 0-based tuple index

    def layerize(
        self,
        nodes: list[dict],
        label_key: str = "item",
        children_key: str = "units",
        level: int = 1,
    ) -> None:
        """Add a `label_key` (defaults to "item") to each node in the
        `nodes` list recursively.

        Recursion happens on every `children_key` (defaults to
        "units) of the node dict. For each level of recursion, use the
        appropriate `ListType`.
        """
        if isinstance(nodes, list):
            flag = False
            for idx, node in enumerate(nodes, start=0):
                if label_key not in node:  # only populate a certain key
                    item_type: ListType = self.get_item_type(level)
                    category: list = item_type.value
                    node[label_key] = f"§{category[idx]}"
                    flag = True  # if any of the siblings requires an `item`, switch
                if node.get(children_key):
                    self.layerize(
                        node[children_key],
                        label_key,
                        children_key,
                        level + 1 if flag else level,
                    )
