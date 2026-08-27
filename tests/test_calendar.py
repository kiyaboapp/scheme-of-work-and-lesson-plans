"""Tests for calendar ingestion API endpoints."""


VALID_CALENDAR_PAYLOAD = {
    "academic_year": "2026",
    "terms": [
        {
            "order": 1,
            "term_id_code": "T1",
            "title": "Term 1",
            "weeks": [
                {
                    "week_number": 1,
                    "start_date": "2026-01-12",
                    "end_date": "2026-01-16",
                    "classification": "teaching",
                    "period_budget": 7,
                    "label": "Week 1",
                },
                {
                    "week_number": 2,
                    "start_date": "2026-01-19",
                    "end_date": "2026-01-23",
                    "classification": "teaching",
                    "period_budget": 7,
                    "label": None,
                },
                {
                    "week_number": 3,
                    "start_date": "2026-03-16",
                    "end_date": "2026-03-20",
                    "classification": "examination",
                    "period_budget": 0,
                    "label": "Mid-term Exam",
                },
            ],
        },
        {
            "order": 2,
            "term_id_code": "T2",
            "title": "Term 2",
            "weeks": [
                {
                    "week_number": 1,
                    "start_date": "2026-04-06",
                    "end_date": "2026-04-10",
                    "classification": "teaching",
                    "period_budget": 7,
                },
                {
                    "week_number": 2,
                    "classification": "holiday",
                    "period_budget": 0,
                    "label": "Easter Break",
                },
            ],
        },
    ],
}


def test_create_calendar_returns_201(client):
    """POST /api/calendar with valid JSON stores data and returns 201."""
    response = client.post("/api/calendar/", json=VALID_CALENDAR_PAYLOAD)
    assert response.status_code == 201

    data = response.json()
    assert data["academic_year"] == "2026"
    assert data["id"] is not None
    assert "created_at" in data

    # Verify nested terms
    assert len(data["terms"]) == 2
    term1 = data["terms"][0]
    assert term1["term_id_code"] == "T1"
    assert term1["title"] == "Term 1"
    assert len(term1["weeks"]) == 3


def test_calendar_weeks_classification_and_budget(client):
    """Test that classification and period_budget are stored correctly."""
    response = client.post("/api/calendar/", json=VALID_CALENDAR_PAYLOAD)
    assert response.status_code == 201

    data = response.json()
    term1_weeks = data["terms"][0]["weeks"]

    # Teaching week
    teaching_week = term1_weeks[0]
    assert teaching_week["classification"] == "teaching"
    assert teaching_week["period_budget"] == 7
    assert teaching_week["week_number"] == 1

    # Examination week
    exam_week = term1_weeks[2]
    assert exam_week["classification"] == "examination"
    assert exam_week["period_budget"] == 0
    assert exam_week["label"] == "Mid-term Exam"

    # Holiday week in term 2
    term2_weeks = data["terms"][1]["weeks"]
    holiday_week = term2_weeks[1]
    assert holiday_week["classification"] == "holiday"
    assert holiday_week["period_budget"] == 0
    assert holiday_week["label"] == "Easter Break"


def test_get_calendar_by_id_returns_nested_structure(client):
    """GET /api/calendar/{id} returns the complete nested structure."""
    create_response = client.post("/api/calendar/", json=VALID_CALENDAR_PAYLOAD)
    assert create_response.status_code == 201
    calendar_id = create_response.json()["id"]

    response = client.get(f"/api/calendar/{calendar_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == calendar_id
    assert data["academic_year"] == "2026"
    assert len(data["terms"]) == 2

    # Verify full depth: calendar > terms > weeks
    term = data["terms"][0]
    assert len(term["weeks"]) == 3
    assert term["weeks"][0]["start_date"] == "2026-01-12"


def test_get_calendar_not_found(client):
    """GET /api/calendar/{id} returns 404 for non-existent ID."""
    response = client.get("/api/calendar/9999")
    assert response.status_code == 404


def test_list_calendars(client):
    """GET /api/calendar lists all calendars."""
    client.post("/api/calendar/", json=VALID_CALENDAR_PAYLOAD)
    client.post(
        "/api/calendar/",
        json={"academic_year": "2027", "terms": []},
    )

    response = client.get("/api/calendar/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    years = [c["academic_year"] for c in data]
    assert "2026" in years
    assert "2027" in years


def test_create_calendar_invalid_classification(client):
    """POST /api/calendar with invalid classification returns 422."""
    payload = {
        "academic_year": "2026",
        "terms": [
            {
                "order": 1,
                "term_id_code": "T1",
                "title": "Term 1",
                "weeks": [
                    {
                        "week_number": 1,
                        "classification": "invalid_type",
                        "period_budget": 7,
                    }
                ],
            }
        ],
    }
    response = client.post("/api/calendar/", json=payload)
    assert response.status_code == 422
