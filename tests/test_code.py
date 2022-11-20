import datetime

import pytest
import yaml

from statute_trees import CodeUnit


@pytest.fixture
def code_obj(shared_datadir) -> dict:
    p = shared_datadir / "codification.yaml"
    return yaml.safe_load(p.read_text())


def test_codification_units_with_history(code_obj):
    assert list(CodeUnit.create_branches(code_obj["units"]))[1].dict(
        exclude_none=True
    ) == {
        "item": "Rule 138",
        "caption": "Attorneys and Admission to Bar",
        "id": "1.2.",
        "units": [
            {
                "item": "Section 5",
                "caption": "Additional requirements for other applicants.",
                "id": "1.2.1.",
                "history": [
                    {
                        "statute_category": "roc",
                        "statute_serial_id": "1940",
                        "locator": "Section 5",
                        "caption": "Additional Requirements for Other Applicants.",
                        "statute": "1940 Rules of Court",
                        "action": "Originated",
                    },
                    {
                        "statute_category": "roc",
                        "statute_serial_id": "1964",
                        "locator": "Section 5",
                        "caption": "Additional requirements for other applicants.",
                        "statute": "1964 Rules of Court",
                        "action": "Originated",
                    },
                    {
                        "statute_category": "rule_bm",
                        "statute_serial_id": "1153",
                        "locator": "Section 5",
                        "caption": "Additional Requirement for Other Applicants.",
                        "statute": "Bar Matter No. 1153",
                        "date": "2010-03-09",
                        "action": "Originated",
                    },
                ],
                "units": [
                    {
                        "item": "Paragraph 1",
                        "content": "(Effective 2023 bar examinations onwards) All applicants for admission other than those referred to in the two preceding sections, shall before being admitted to the examination, satisfactorily show that they have successfully completed all the prescribed courses for the degree of Bachelor of Laws or its equivalent degree, in a law school or university officially recognized by the Philippine Government or by the proper authority in the foreign jurisdiction where the degree has been granted.",
                        "id": "1.2.1.1.",
                        "units": [],
                    },
                    {
                        "item": "Paragraph 2",
                        "content": "No applicant who obtained the Bachelor of Laws degree in this jurisdiction shall be admitted to the bar examination unless he or she has satisfactorily completed the following course in a law school or university duly recognized by the government: civil law, commercial law, remedial law, criminal law, public and private international law, political law, labor and social legislation medical jurisprudence, taxation, legal ethics and clinical legal education program.",
                        "id": "1.2.1.2.",
                        "units": [],
                    },
                    {
                        "item": "Paragraph 3",
                        "content": "A Filipino citizen who graduated from a foreign law school shall be admitted to the bar examination only upon submission to the Supreme Court of certifications showing: (a) completion of all courses leading to the degree of Bachelor of Laws or its equivalent degree; (b) recognition or accreditation of the law school by the proper authority; and (c) completion of all the fourth year subjects in the Bachelor of Laws academic program in a law school duly recognized by the Philippine Government. (As amended by B.M. No. 1153, March 09, 2010)",
                        "id": "1.2.1.3.",
                        "units": [],
                    },
                ],
            }
        ],
    }
