from pathlib import Path

import pytest
import yaml

from statute_trees import StatuteUnit


@pytest.fixture
def titled_obj(shared_datadir) -> dict:
    p = shared_datadir / "titled.yaml"
    return yaml.safe_load(p.read_text())


def test_title_set(titled_obj):
    title = "The Judiciary Reorganization Act of 1980"
    objects = list(StatuteUnit.create_branches(titled_obj["units"]))
    matched = StatuteUnit.get_first_title(objects)
    assert matched == title
