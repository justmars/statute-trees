import pytest
import yaml

from statute_trees import StatuteUnit


@pytest.fixture
def statute_obj(shared_datadir) -> dict:
    p = shared_datadir / "statute.yaml"
    return yaml.safe_load(p.read_text())


@pytest.fixture
def statute_units() -> list[StatuteUnit]:
    return [
        StatuteUnit(
            item="Chapter I",
            caption="General Provisions.",
            content=None,
            id="1.1.",
            units=[
                StatuteUnit(
                    item="Section 1",
                    caption=(
                        "Courts of justice to be maintained in every province."
                    ),
                    content=(
                        "Courts of justice shall be maintained in every"
                        " province in the Philippine Islands in which civil"
                        " government shall be established; which courts shall"
                        " be open for the trial of all causes proper for their"
                        " cognizance, and justice shall be therein impartially"
                        " administered without corruption or unnecessary"
                        " delay."
                    ),
                    id="1.1.1.",
                    units=[],
                ),
                StatuteUnit(
                    item="Section 2",
                    caption="Constitution of judiciary",
                    content=(
                        "The judicial power of the Government of the"
                        " Philippine Islands shall be vested in a Supreme"
                        " Court, Courts of First instance, and courts of"
                        " justices of the peace, together with such special"
                        " jurisdictions of municipal courts, and other special"
                        " tribunals as now are or hereafter may be authorized"
                        " by law. The two courts first named shall be courts"
                        " of record."
                    ),
                    id="1.1.2.",
                    units=[],
                ),
            ],
        )
    ]


def test_statute_unit_create_branches(statute_obj, statute_units):
    units_from_branch = list(StatuteUnit.create_branches(statute_obj["units"]))
    assert units_from_branch == statute_units


def test_statute_unit_material_paths(statute_units):
    assert list(StatuteUnit.granularize("pk_923452", statute_units)) == [
        {
            "item": "Chapter I",
            "caption": "General Provisions.",
            "content": None,
            "units": [
                {
                    "item": "Section 1",
                    "caption": (
                        "Courts of justice to be maintained in every province."
                    ),
                    "content": (
                        "Courts of justice shall be maintained in every"
                        " province in the Philippine Islands in which civil"
                        " government shall be established; which courts shall"
                        " be open for the trial of all causes proper for their"
                        " cognizance, and justice shall be therein impartially"
                        " administered without corruption or unnecessary"
                        " delay."
                    ),
                    "id": "1.1.1.",
                    "units": [],
                },
                {
                    "item": "Section 2",
                    "caption": "Constitution of judiciary",
                    "content": (
                        "The judicial power of the Government of the"
                        " Philippine Islands shall be vested in a Supreme"
                        " Court, Courts of First instance, and courts of"
                        " justices of the peace, together with such special"
                        " jurisdictions of municipal courts, and other special"
                        " tribunals as now are or hereafter may be authorized"
                        " by law. The two courts first named shall be courts"
                        " of record."
                    ),
                    "id": "1.1.2.",
                    "units": [],
                },
            ],
            "statute_id": "pk_923452",
            "material_path": "1.1.",
        },
        {
            "item": "Section 1",
            "caption": "Courts of justice to be maintained in every province.",
            "content": (
                "Courts of justice shall be maintained in every province in"
                " the Philippine Islands in which civil government shall be"
                " established; which courts shall be open for the trial of all"
                " causes proper for their cognizance, and justice shall be"
                " therein impartially administered without corruption or"
                " unnecessary delay."
            ),
            "units": [],
            "statute_id": "pk_923452",
            "material_path": "1.1.1.",
        },
        {
            "item": "Section 2",
            "caption": "Constitution of judiciary",
            "content": (
                "The judicial power of the Government of the Philippine"
                " Islands shall be vested in a Supreme Court, Courts of First"
                " instance, and courts of justices of the peace, together with"
                " such special jurisdictions of municipal courts, and other"
                " special tribunals as now are or hereafter may be authorized"
                " by law. The two courts first named shall be courts of"
                " record."
            ),
            "units": [],
            "statute_id": "pk_923452",
            "material_path": "1.1.2.",
        },
    ]


def test_statute_unit_searchables(statute_units):
    assert list(StatuteUnit.searchables("pk_923452", statute_units)) == [
        {
            "material_path": "1.1.",
            "statute_id": "pk_923452",
            "unit_text": "General Provisions.",
        },
        {
            "material_path": "1.1.1.",
            "statute_id": "pk_923452",
            "unit_text": (
                "Courts of justice to be maintained in every province.. Courts"
                " of justice shall be maintained in every province in the"
                " Philippine Islands in which civil government shall be"
                " established; which courts shall be open for the trial of all"
                " causes proper for their cognizance, and justice shall be"
                " therein impartially administered without corruption or"
                " unnecessary delay."
            ),
        },
        {
            "material_path": "1.1.2.",
            "statute_id": "pk_923452",
            "unit_text": (
                "Constitution of judiciary. The judicial power of the"
                " Government of the Philippine Islands shall be vested in a"
                " Supreme Court, Courts of First instance, and courts of"
                " justices of the peace, together with such special"
                " jurisdictions of municipal courts, and other special"
                " tribunals as now are or hereafter may be authorized by law."
                " The two courts first named shall be courts of record."
            ),
        },
    ]
