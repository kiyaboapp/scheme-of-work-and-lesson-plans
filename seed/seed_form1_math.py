"""
Seed script for Form I Mathematics data.

Populates the database with the complete Form I Mathematics syllabus
(extracted from the Tanzania O-Level Mathematics Syllabus 2023),
the 2026 academic calendar (matching the sample scheme dates),
textbook entries, and runs the allocation engine.

Usage:
    cd /projects/sandbox/scheme-of-work-and-lesson-plans
    .venv/bin/python seed/seed_form1_math.py
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


# ---------------------------------------------------------------------------
# Form I Mathematics Syllabus Data (from pages 14-24 of the syllabus)
# Total: 175 periods (30 + 36 + 34 + 45 + 30)
# ---------------------------------------------------------------------------

SYLLABUS_DATA = {
    "subject": "Basic Mathematics",
    "form": "Form I",
    "source_note": "TIE (2023), Mathematics Syllabus for Ordinary Secondary Education Form I-IV",
    "topics": [
        {
            "order": 1,
            "topic_id_code": "1.0",
            "title": "Demonstrate mastery of mathematical language",
            "sub_topics": [
                {
                    "order": 1,
                    "sub_topic_id_code": "1.1",
                    "title": "Use numerical skills in different contexts",
                    "planned_periods": 30,
                    "competences": [
                        "Explain the basic concepts of Mathematics",
                        "Explain the concept of rational, irrational, and real numbers",
                        "Represent rational numbers on a number line",
                        "Explain the concept of inequalities and absolute values of real numbers",
                        "Describe the importance of numbers in real-life situations",
                    ],
                    "objectives": [
                        {
                            "order": 1,
                            "text": (
                                "(a) Explain the basic concepts of Mathematics "
                                "(Meaning of mathematics, branches of mathematics, "
                                "relationship between mathematics and other subjects, "
                                "importance of mathematics)"
                            ),
                        },
                        {
                            "order": 2,
                            "text": (
                                "(b) Explain the concept of rational, irrational, "
                                "and real numbers"
                            ),
                        },
                        {
                            "order": 3,
                            "text": (
                                "(c) Represent rational numbers on a number line"
                            ),
                        },
                        {
                            "order": 4,
                            "text": (
                                "(d) Explain the concept of inequalities and "
                                "absolute values of real numbers"
                            ),
                        },
                        {
                            "order": 5,
                            "text": (
                                "(e) Describe the importance of numbers in "
                                "real-life situations"
                            ),
                        },
                    ],
                },
                {
                    "order": 2,
                    "sub_topic_id_code": "1.2",
                    "title": "Use ratios and proportions in daily life",
                    "planned_periods": 36,
                    "competences": [
                        "Explain the concept of ratios and proportions",
                        "Solve ratio and proportion problems",
                    ],
                    "objectives": [
                        {
                            "order": 1,
                            "text": (
                                "(a) Explain the concept of ratios and proportions"
                            ),
                        },
                        {
                            "order": 2,
                            "text": (
                                "(b) Solve ratio and proportion problems"
                            ),
                        },
                    ],
                },
            ],
        },
        {
            "order": 2,
            "topic_id_code": "2.0",
            "title": "Demonstrate mastery of basic concepts in geometry and algebra",
            "sub_topics": [
                {
                    "order": 1,
                    "sub_topic_id_code": "2.1",
                    "title": (
                        "Use geometry, approximations, relations and functions "
                        "in various contexts"
                    ),
                    "planned_periods": 34,
                    "competences": [
                        "Explain the concept of approximations",
                        "Round off numbers and estimate values of expressions",
                        "Approximate numbers to the required significant figures and decimal places",
                        "Use approximations in computations and measurements of quantities in various contexts",
                    ],
                    "objectives": [
                        {
                            "order": 1,
                            "text": (
                                "(a) Explain the concept of approximations "
                                "(rounding off, significant figures, and decimal places)"
                            ),
                        },
                        {
                            "order": 2,
                            "text": (
                                "(b) Round off numbers and estimate values of expressions"
                            ),
                        },
                        {
                            "order": 3,
                            "text": (
                                "(c) Approximate numbers to the required significant "
                                "figures and decimal places"
                            ),
                        },
                        {
                            "order": 4,
                            "text": (
                                "(d) Use approximations in computations and measurements "
                                "of quantities in various contexts"
                            ),
                        },
                    ],
                },
                {
                    "order": 2,
                    "sub_topic_id_code": "2.2",
                    "title": "Use algebra and matrices in problem solving",
                    "planned_periods": 45,
                    "competences": [
                        "Explore the basic tenets of algebra",
                        "Use algebraic expressions to model situations",
                        "Solve simultaneous equations using substitution and elimination methods",
                        "Solve inequalities in one unknown",
                    ],
                    "objectives": [
                        {
                            "order": 1,
                            "text": (
                                "(a) Explore the basic tenets of algebra "
                                "(algebraic expressions and equations, linear "
                                "simultaneous equations of two unknowns, "
                                "inequalities in one unknown)"
                            ),
                        },
                        {
                            "order": 2,
                            "text": (
                                "(b) Use algebraic expressions to model situations "
                                "(word problems into algebraic expressions and equations)"
                            ),
                        },
                        {
                            "order": 3,
                            "text": (
                                "(c) Solve simultaneous equations using substitution "
                                "and elimination methods"
                            ),
                        },
                        {
                            "order": 4,
                            "text": (
                                "(d) Solve inequalities in one unknown"
                            ),
                        },
                    ],
                },
            ],
        },
        {
            "order": 3,
            "topic_id_code": "3.0",
            "title": (
                "Demonstrate mastery of basic concepts in coordinate geometry, "
                "trigonometry, circles, vectors, probability and statistics"
            ),
            "sub_topics": [
                {
                    "order": 1,
                    "sub_topic_id_code": "3.1",
                    "title": (
                        "Use basic coordinate geometry, trigonometry and vectors "
                        "skills in daily life"
                    ),
                    "planned_periods": 30,
                    "competences": [
                        "Explore the basic tenets of coordinate geometry",
                        "Find the gradient/slope of a line",
                        "Determine the equation of a straight line and draw its graph",
                        "Solve linear simultaneous equations graphically",
                        "Use mathematical software to solve and draw graphs of simultaneous equations",
                    ],
                    "objectives": [
                        {
                            "order": 1,
                            "text": (
                                "(a) Explore the basic tenets of coordinate geometry "
                                "(gradient and equations of a straight line, graphs "
                                "of linear equations)"
                            ),
                        },
                        {
                            "order": 2,
                            "text": (
                                "(b) Find the gradient/slope of a line"
                            ),
                        },
                        {
                            "order": 3,
                            "text": (
                                "(c) Determine the equation of a straight line "
                                "and draw its graph"
                            ),
                        },
                        {
                            "order": 4,
                            "text": (
                                "(d) Solve linear simultaneous equations graphically"
                            ),
                        },
                        {
                            "order": 5,
                            "text": (
                                "(e) Use mathematical software to solve and draw "
                                "graphs of simultaneous equations"
                            ),
                        },
                    ],
                },
            ],
        },
    ],
}


# ---------------------------------------------------------------------------
# 2026 Academic Calendar (matching the sample scheme dates)
# 5 periods per week, 35 teaching weeks needed for 175 periods
# Term 1: 15 teaching weeks (March - June 2026)
# Term 2: 20 teaching weeks (July - November 2026)
# ---------------------------------------------------------------------------

CALENDAR_DATA = {
    "academic_year": "2026",
    "terms": [
        {
            "order": 1,
            "term_id_code": "T1",
            "title": "First Term 2026",
            "weeks": [
                # Registration & Orientation (Jan-Feb)
                {
                    "week_number": 1,
                    "start_date": "2026-01-13",
                    "end_date": "2026-02-28",
                    "classification": "holiday",
                    "period_budget": 0,
                    "label": "Registration & Orientation 13/01/2026 - 28/02/2026",
                },
                # Teaching weeks - March
                {
                    "week_number": 2,
                    "start_date": "2026-03-02",
                    "end_date": "2026-03-06",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "March Week 1",
                },
                {
                    "week_number": 3,
                    "start_date": "2026-03-09",
                    "end_date": "2026-03-13",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "March Week 2",
                },
                {
                    "week_number": 4,
                    "start_date": "2026-03-16",
                    "end_date": "2026-03-20",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "March Week 3",
                },
                {
                    "week_number": 5,
                    "start_date": "2026-03-23",
                    "end_date": "2026-03-27",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "March Week 4",
                },
                # Mid-term assessment
                {
                    "week_number": 6,
                    "start_date": "2026-03-27",
                    "end_date": "2026-03-27",
                    "classification": "examination",
                    "period_budget": 0,
                    "label": "Mid-term Assessment",
                },
                # Mid-term break
                {
                    "week_number": 7,
                    "start_date": "2026-03-27",
                    "end_date": "2026-04-08",
                    "classification": "holiday",
                    "period_budget": 0,
                    "label": "Mid-term Break 27/03/2026 - 08/04/2026",
                },
                # Teaching weeks - April
                {
                    "week_number": 8,
                    "start_date": "2026-04-09",
                    "end_date": "2026-04-13",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "April Week 1",
                },
                {
                    "week_number": 9,
                    "start_date": "2026-04-14",
                    "end_date": "2026-04-18",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "April Week 2",
                },
                {
                    "week_number": 10,
                    "start_date": "2026-04-20",
                    "end_date": "2026-04-25",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "April Week 3",
                },
                {
                    "week_number": 11,
                    "start_date": "2026-04-27",
                    "end_date": "2026-05-01",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "April Week 4",
                },
                # Teaching weeks - May
                {
                    "week_number": 12,
                    "start_date": "2026-05-04",
                    "end_date": "2026-05-08",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "May Week 1",
                },
                {
                    "week_number": 13,
                    "start_date": "2026-05-11",
                    "end_date": "2026-05-15",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "May Week 2",
                },
                {
                    "week_number": 14,
                    "start_date": "2026-05-18",
                    "end_date": "2026-05-22",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "May Week 3",
                },
                {
                    "week_number": 15,
                    "start_date": "2026-05-25",
                    "end_date": "2026-05-29",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "May Week 4",
                },
                # Teaching weeks - June
                {
                    "week_number": 16,
                    "start_date": "2026-06-01",
                    "end_date": "2026-06-05",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "June Week 1",
                },
                {
                    "week_number": 17,
                    "start_date": "2026-06-08",
                    "end_date": "2026-06-12",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "June Week 2",
                },
                {
                    "week_number": 18,
                    "start_date": "2026-06-15",
                    "end_date": "2026-06-19",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "June Week 3",
                },
                # Terminal assessment
                {
                    "week_number": 19,
                    "start_date": "2026-06-22",
                    "end_date": "2026-06-26",
                    "classification": "examination",
                    "period_budget": 0,
                    "label": "Terminal Assessment",
                },
                # First term break
                {
                    "week_number": 20,
                    "start_date": "2026-06-26",
                    "end_date": "2026-07-06",
                    "classification": "holiday",
                    "period_budget": 0,
                    "label": "First Term Break 05/06/2026 - 06/07/2026",
                },
            ],
        },
        {
            "order": 2,
            "term_id_code": "T2",
            "title": "Second Term 2026",
            "weeks": [
                # Teaching weeks - July
                {
                    "week_number": 1,
                    "start_date": "2026-07-06",
                    "end_date": "2026-07-10",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "July Week 1",
                },
                {
                    "week_number": 2,
                    "start_date": "2026-07-13",
                    "end_date": "2026-07-17",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "July Week 2",
                },
                {
                    "week_number": 3,
                    "start_date": "2026-07-20",
                    "end_date": "2026-07-24",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "July Week 3",
                },
                {
                    "week_number": 4,
                    "start_date": "2026-07-27",
                    "end_date": "2026-07-31",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "July Week 4",
                },
                # Teaching weeks - August
                {
                    "week_number": 5,
                    "start_date": "2026-08-03",
                    "end_date": "2026-08-07",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "August Week 1",
                },
                {
                    "week_number": 6,
                    "start_date": "2026-08-10",
                    "end_date": "2026-08-14",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "August Week 2",
                },
                {
                    "week_number": 7,
                    "start_date": "2026-08-17",
                    "end_date": "2026-08-21",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "August Week 3",
                },
                {
                    "week_number": 8,
                    "start_date": "2026-08-24",
                    "end_date": "2026-08-28",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "August Week 4",
                },
                {
                    "week_number": 9,
                    "start_date": "2026-08-31",
                    "end_date": "2026-09-04",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "September Week 1",
                },
                # Mid-term assessment
                {
                    "week_number": 10,
                    "start_date": "2026-09-04",
                    "end_date": "2026-09-04",
                    "classification": "examination",
                    "period_budget": 0,
                    "label": "Mid-term Assessment",
                },
                # Mid-term break
                {
                    "week_number": 11,
                    "start_date": "2026-09-04",
                    "end_date": "2026-09-14",
                    "classification": "holiday",
                    "period_budget": 0,
                    "label": "Mid-term Break 04/09/2026 - 14/09/2026",
                },
                # Teaching weeks - September/October/November
                {
                    "week_number": 12,
                    "start_date": "2026-09-14",
                    "end_date": "2026-09-18",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "September Week 3",
                },
                {
                    "week_number": 13,
                    "start_date": "2026-09-21",
                    "end_date": "2026-09-25",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "September Week 4",
                },
                {
                    "week_number": 14,
                    "start_date": "2026-09-28",
                    "end_date": "2026-10-02",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "October Week 1",
                },
                {
                    "week_number": 15,
                    "start_date": "2026-10-05",
                    "end_date": "2026-10-09",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "October Week 2",
                },
                {
                    "week_number": 16,
                    "start_date": "2026-10-12",
                    "end_date": "2026-10-16",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "October Week 3",
                },
                {
                    "week_number": 17,
                    "start_date": "2026-10-19",
                    "end_date": "2026-10-23",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "October Week 4",
                },
                {
                    "week_number": 18,
                    "start_date": "2026-10-26",
                    "end_date": "2026-10-30",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "November Week 1",
                },
                {
                    "week_number": 19,
                    "start_date": "2026-11-02",
                    "end_date": "2026-11-06",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "November Week 2",
                },
                {
                    "week_number": 20,
                    "start_date": "2026-11-09",
                    "end_date": "2026-11-13",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "November Week 3",
                },
                {
                    "week_number": 21,
                    "start_date": "2026-11-16",
                    "end_date": "2026-11-20",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "November Week 4",
                },
                {
                    "week_number": 22,
                    "start_date": "2026-11-23",
                    "end_date": "2026-11-27",
                    "classification": "teaching",
                    "period_budget": 5,
                    "label": "November Week 5",
                },
                # Revision and annual assessment
                {
                    "week_number": 23,
                    "start_date": "2026-11-30",
                    "end_date": "2026-12-04",
                    "classification": "examination",
                    "period_budget": 0,
                    "label": "Revision and Annual Assessment",
                },
                # End of year break
                {
                    "week_number": 24,
                    "start_date": "2026-12-04",
                    "end_date": "2026-12-31",
                    "classification": "holiday",
                    "period_budget": 0,
                    "label": "End of Year Break 04/12/2026",
                },
            ],
        },
    ],
}

# Textbook reference used throughout the sample scheme
TEXTBOOK_REFERENCE = "TIE (2023), Basic Mathematics for Secondary Schools Book 1, TIE-DSM"


def run_seed():
    """Run the seed process using FastAPI TestClient."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    client = TestClient(app)

    print("=" * 60)
    print("  SEED: Form I Mathematics 2026")
    print("=" * 60)

    # ---- Step 1: Create Syllabus ----
    print("\n[1/4] Creating syllabus...")
    resp = client.post("/api/syllabus/", json=SYLLABUS_DATA)
    if resp.status_code != 201:
        print(f"  ERROR creating syllabus: {resp.status_code} - {resp.text}")
        sys.exit(1)
    syllabus = resp.json()
    syllabus_id = syllabus["id"]
    topic_count = len(syllabus["topics"])
    sub_topic_count = sum(len(t["sub_topics"]) for t in syllabus["topics"])
    total_periods = sum(
        st["planned_periods"]
        for t in syllabus["topics"]
        for st in t["sub_topics"]
    )
    print(f"  Created syllabus id={syllabus_id}")
    print(f"  Topics: {topic_count}, Sub-topics: {sub_topic_count}")
    print(f"  Total planned periods: {total_periods}")

    # ---- Step 2: Create Calendar ----
    print("\n[2/4] Creating calendar...")
    resp = client.post("/api/calendar/", json=CALENDAR_DATA)
    if resp.status_code != 201:
        print(f"  ERROR creating calendar: {resp.status_code} - {resp.text}")
        sys.exit(1)
    calendar = resp.json()
    calendar_id = calendar["id"]
    term_count = len(calendar["terms"])
    teaching_weeks = sum(
        1
        for t in calendar["terms"]
        for w in t["weeks"]
        if w["classification"] == "teaching"
    )
    total_budget = sum(
        w["period_budget"] or 0
        for t in calendar["terms"]
        for w in t["weeks"]
        if w["classification"] == "teaching"
    )
    print(f"  Created calendar id={calendar_id}")
    print(f"  Terms: {term_count}, Teaching weeks: {teaching_weeks}")
    print(f"  Total period budget: {total_budget}")

    # ---- Step 3: Create Textbook Entries ----
    print("\n[3/4] Creating textbook entries...")
    # Collect all sub-topic IDs
    sub_topic_ids = [
        st["id"]
        for t in syllabus["topics"]
        for st in t["sub_topics"]
    ]
    textbook_entries = [
        {
            "sub_topic_id": st_id,
            "book_title": TEXTBOOK_REFERENCE,
            "start_page": None,
            "end_page": None,
            "note": None,
        }
        for st_id in sub_topic_ids
    ]
    resp = client.post("/api/textbook/", json=textbook_entries)
    if resp.status_code != 201:
        print(f"  ERROR creating textbook entries: {resp.status_code} - {resp.text}")
        sys.exit(1)
    textbooks = resp.json()
    print(f"  Created {len(textbooks)} textbook entries")

    # ---- Step 4: Run Allocation ----
    print("\n[4/4] Running allocation...")
    resp = client.post(
        "/api/allocate",
        json={"syllabus_id": syllabus_id, "calendar_id": calendar_id},
    )
    if resp.status_code != 200:
        print(f"  ERROR running allocation: {resp.status_code} - {resp.text}")
        sys.exit(1)
    allocation = resp.json()
    assignment_count = len(allocation["assignments"])
    total_allocated = sum(a["periods"] for a in allocation["assignments"])
    print(f"  Created {assignment_count} allocation assignments")
    print(f"  Total periods allocated: {total_allocated}")

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("  SEED COMPLETE")
    print("=" * 60)
    print(f"  Syllabus:    id={syllabus_id} ({topic_count} topics, {sub_topic_count} sub-topics)")
    print(f"  Calendar:    id={calendar_id} ({term_count} terms, {teaching_weeks} teaching weeks)")
    print(f"  Textbooks:   {len(textbooks)} entries")
    print(f"  Allocation:  {assignment_count} assignments ({total_allocated}/{total_periods} periods)")
    if total_allocated == total_periods:
        print("  Status:      ALL periods allocated successfully!")
    else:
        print(f"  WARNING:     {total_periods - total_allocated} periods unallocated!")
    print("=" * 60)

    return {
        "syllabus_id": syllabus_id,
        "calendar_id": calendar_id,
        "assignments": assignment_count,
        "total_allocated": total_allocated,
        "total_planned": total_periods,
    }


if __name__ == "__main__":
    run_seed()
