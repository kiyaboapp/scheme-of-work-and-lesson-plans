"""Tests for the scheme of work generation endpoint."""


def _setup_and_allocate(client):
    """Create syllabus, calendar, and run allocation."""
    syllabus_data = {
        "subject": "Mathematics",
        "form": "Form 1",
        "topics": [
            {
                "order": 1,
                "topic_id_code": "T1",
                "title": "Numbers",
                "sub_topics": [
                    {
                        "order": 1,
                        "sub_topic_id_code": "T1.1",
                        "title": "Natural Numbers",
                        "planned_periods": 5,
                        "objectives": [
                            {"order": 1, "text": "Count natural numbers"},
                            {"order": 2, "text": "Identify place values"},
                        ],
                    },
                    {
                        "order": 2,
                        "sub_topic_id_code": "T1.2",
                        "title": "Integers",
                        "planned_periods": 7,
                        "objectives": [
                            {"order": 1, "text": "Add integers"},
                        ],
                    },
                ],
            },
        ],
    }

    calendar_data = {
        "academic_year": "2026",
        "terms": [
            {
                "order": 1,
                "term_id_code": "T1",
                "title": "Term 1",
                "weeks": [
                    {
                        "week_number": 1,
                        "start_date": "2026-01-05",
                        "end_date": "2026-01-09",
                        "classification": "teaching",
                        "period_budget": 5,
                        "label": "Week 1",
                    },
                    {
                        "week_number": 2,
                        "start_date": "2026-01-12",
                        "end_date": "2026-01-16",
                        "classification": "teaching",
                        "period_budget": 5,
                        "label": "Week 2",
                    },
                    {
                        "week_number": 3,
                        "start_date": "2026-01-19",
                        "end_date": "2026-01-23",
                        "classification": "teaching",
                        "period_budget": 5,
                        "label": "Week 3",
                    },
                ],
            },
        ],
    }

    syl_resp = client.post("/api/syllabus", json=syllabus_data)
    assert syl_resp.status_code == 201
    syllabus_id = syl_resp.json()["id"]

    cal_resp = client.post("/api/calendar", json=calendar_data)
    assert cal_resp.status_code == 201
    calendar_id = cal_resp.json()["id"]

    alloc_resp = client.post("/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id})
    assert alloc_resp.status_code == 200

    return syllabus_id, calendar_id


def test_scheme_returns_correct_structure(client):
    """Scheme endpoint returns entries with all required fields."""
    syllabus_id, calendar_id = _setup_and_allocate(client)

    resp = client.get(f"/api/scheme/{syllabus_id}/{calendar_id}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["syllabus_id"] == syllabus_id
    assert data["calendar_id"] == calendar_id
    assert data["subject"] == "Mathematics"
    assert data["form"] == "Form 1"
    assert data["academic_year"] == "2026"
    assert len(data["entries"]) > 0

    # Check first entry has all fields
    entry = data["entries"][0]
    assert "week_number" in entry
    assert "term" in entry
    assert "topic_title" in entry
    assert "sub_topic_title" in entry
    assert "objectives" in entry
    assert "periods" in entry
    assert "teaching_methods" in entry
    assert "teaching_resources" in entry
    assert "references" in entry


def test_scheme_entries_in_order(client):
    """Scheme entries should be ordered by week_number then slot."""
    syllabus_id, calendar_id = _setup_and_allocate(client)

    resp = client.get(f"/api/scheme/{syllabus_id}/{calendar_id}")
    assert resp.status_code == 200
    data = resp.json()

    entries = data["entries"]
    week_numbers = [e["week_number"] for e in entries]
    # Week numbers should be non-decreasing
    assert week_numbers == sorted(week_numbers)


def test_scheme_includes_split_info(client):
    """Split sub-topics should show '(Part X/Y)' suffix in title."""
    syllabus_id, calendar_id = _setup_and_allocate(client)

    resp = client.get(f"/api/scheme/{syllabus_id}/{calendar_id}")
    assert resp.status_code == 200
    data = resp.json()

    # Integers has 7 periods, budget is 5 per week. After Natural Numbers fills week 1,
    # Integers should be split across week 2 and week 3
    entries = data["entries"]
    split_entries = [e for e in entries if "(Part" in e["sub_topic_title"]]
    assert len(split_entries) >= 2, f"Expected split entries, got: {[e['sub_topic_title'] for e in entries]}"

    # Check format
    for entry in split_entries:
        assert "Part" in entry["sub_topic_title"]
        assert "/" in entry["sub_topic_title"]
