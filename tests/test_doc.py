import pytest
import yaml

from statute_trees import DocUnit
from statute_trees.resources import EventStatute


@pytest.fixture
def doc_obj(shared_datadir) -> dict:
    p = shared_datadir / "document.yaml"
    return yaml.safe_load(p.read_text())


def test_event_source():
    text = """
    - locator: 8
      statute: Executive Order No. 292
      content: The powers expressly vested in any branch of the Government
    """
    objs = yaml.safe_load(text)
    obj = objs[0]
    assert EventStatute(**obj).dict(exclude_none=True) == {
        "statute_category": "eo",
        "statute_serial_id": "292",
        "locator": "8",  # converted to string
        "content": "The powers expressly vested in any branch of the Government",
        "statute": "Executive Order No. 292",
    }


def test_document_units_with_layers_and_sources(doc_obj):
    assert list(DocUnit.create_branches(doc_obj["units"]))[0].dict(
        exclude_none=True
    ) == {
        "item": "§I",
        "caption": "Governance",
        "id": "1.1.",
        "units": [
            {
                "item": "§A",
                "caption": "Separation of Powers",
                "id": "1.1.1.",
                "units": [
                    {
                        "item": "§1",
                        "caption": "Concept",
                        "id": "1.1.1.1.",
                        "sources": [
                            {
                                "statute_category": "eo",
                                "statute_serial_id": "292",
                                "locator": "8",
                                "content": "The powers expressly vested in any branch of the Government",
                                "statute": "Executive Order No. 292",
                            },
                            {
                                "query": '"separation of powers" AND (  (    "branches of government" OR    "undue concentration of powers"  )  OR (    "prevent despotism"  ) OR  (    (legislature enacts) AND    (judiciary interprets) AND    (executive implements)  ))'
                            },
                        ],
                        "units": [
                            {
                                "item": "Paragraph 1",
                                "content": "The powers expressly vested in any branch of the Government shall not be exercised by, nor delegated to, any other branch of the Government, except to the extent authorized by the Constitution.",
                                "id": "1.1.1.1.1.",
                                "units": [],
                            },
                            {
                                "item": "Paragraph 2",
                                "content": "The separation of powers is a fundamental principle in the Philippine system of government. It obtains not through express provision but by actual division in the Constitution. Each department of the government has exclusive cognizance of matters within its jurisdiction, and is supreme within its own sphere.",
                                "id": "1.1.1.1.2.",
                                "units": [],
                            },
                            {
                                "item": "Paragraph 3",
                                "content": "Under the principle of separation of powers, neither Congress, the President, nor the Judiciary may encroach on fields allocated to the other branches of government. The legislature is generally limited to the enactment of laws, the executive to the enforcement of laws, and the judiciary to their interpretation and application to cases and controversies.",
                                "id": "1.1.1.1.3.",
                                "units": [],
                            },
                            {
                                "item": "Paragraph 4",
                                "content": 'The theory of the separation of powers is designed by its originators to secure action and at the same time to forestall over action which necessarily results from undue concentration of powers, and thereby obtain efficiency and prevent despotism.  Thereby, the "rule of law" was established which narrows the range of governmental action and makes it subject to control by certain legal devices.',
                                "id": "1.1.1.1.4.",
                                "units": [],
                            },
                        ],
                    }
                ],
            }
        ],
    }
