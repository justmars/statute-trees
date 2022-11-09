import datetime

import pytest
from statute_patterns import StatuteTitle

from statute_trees import StatutePage, StatuteUnit


@pytest.fixture
def raw_const(shared_datadir):
    return StatutePage.build(
        shared_datadir / "statutes" / "const" / "1987" / "details.yaml"
    )


def test_id(raw_const: StatutePage):
    assert raw_const.id == "const-1987-october-15-1986"


def test_raw_statute_base(raw_const: StatutePage):
    assert raw_const.statute_category == "const"
    assert raw_const.statute_serial_id == "1987"


def test_date(raw_const: StatutePage):
    assert raw_const.date == datetime.date(1986, 10, 15)


def test_nested_statute_units(raw_const):
    assert isinstance(raw_const.tree, list)
    assert len(raw_const.tree) == 1
    assert isinstance(raw_const.tree[0], StatuteUnit)
    assert isinstance(raw_const.units, str)


def test_titles(raw_const):
    assert isinstance(raw_const.titles, list)
    assert len(raw_const.titles) == 4
    assert isinstance(raw_const.titles[0], StatuteTitle)
