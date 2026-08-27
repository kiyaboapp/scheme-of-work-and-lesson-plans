"""Tests for the lesson plan generation endpoints."""


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


def test_lesson_plan_for_valid_period(client):
    """Retrieving a lesson plan for a valid period returns correct data."""
    syllabus_id, calendar_id = _setup_and_allocate(client)

    resp = client.get(f"/api/lesson-plan/{syllabus_id}/{calendar_id}/week/1/period/1")
    assert resp.status_code == 200
    data = resp.json()

    assert data["period_number"] == 1
    assert data["date"] == "2026-01-05"  # start_date + 0 days for period 1
    assert "Count natural numbers" in data["teacher_activities"]
    assert data["student_activities"] is not None
    assert data["assessment"] is not None
    assert "Natural Numbers" in data["consolidation"]
    assert data["teaching_resources"] is not None


def test_lesson_plan_for_invalid_week(client):
    """Requesting a lesson plan for a non-existent week returns 404."""
    syllabus_id, calendar_id = _setup_and_allocate(client)

    resp = client.get(f"/api/lesson-plan/{syllabus_id}/{calendar_id}/week/99/period/1")
    assert resp.status_code == 404


def test_lesson_plan_for_full_week(client):
    """Requesting all lesson plans for a week returns one plan per assigned period."""
    syllabus_id, calendar_id = _setup_and_allocate(client)

    resp = client.get(f"/api/lesson-plan/{syllabus_id}/{calendar_id}/week/1")
    assert resp.status_code == 200
    data = resp.json()

    # Week 1 has budget of 5 and sub-topic has 5 planned_periods
    assert len(data) == 5

    # Each plan should have a unique period number
    period_numbers = [plan["period_number"] for plan in data]
    assert sorted(period_numbers) == [1, 2, 3, 4, 5]

    # Dates should increment from start_date
    dates = [plan["date"] for plan in data]
    assert dates[0] == "2026-01-05"
    assert dates[1] == "2026-01-06"
    assert dates[2] == "2026-01-07"
    assert dates[3] == "2026-01-08"
    assert dates[4] == "2026-01-09"
