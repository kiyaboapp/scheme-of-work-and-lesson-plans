"""Tests verifying the review fixes (allocation idempotency, FK validation, date derivation, etc.)."""


def _create_syllabus_and_calendar(client, period_budget=5):
    """Helper to create test data with configurable period_budget per week."""
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
                        "planned_periods": period_budget,
                        "competences": ["Counting", "Problem solving"],
                        "objectives": [
                            {"order": 1, "text": "Count natural numbers"},
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
                        "period_budget": period_budget,
                        "label": "Week 1",
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

    return syllabus_id, calendar_id


class TestAllocationIdempotency:
    """Tests for fix #1: duplicate allocations on re-run."""

    def test_second_allocation_replaces_first(self, client):
        """POST /api/allocate a second time should replace (not append) assignments."""
        syllabus_id, calendar_id = _create_syllabus_and_calendar(client)

        # First allocation
        resp1 = client.post(
            "/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id}
        )
        assert resp1.status_code == 200
        count1 = len(resp1.json()["assignments"])

        # Second allocation on same pair
        resp2 = client.post(
            "/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id}
        )
        assert resp2.status_code == 200
        count2 = len(resp2.json()["assignments"])

        # Should be same count, not doubled
        assert count2 == count1

    def test_get_allocation_after_rerun_not_doubled(self, client):
        """GET allocation after two POST calls should show single set of assignments."""
        syllabus_id, calendar_id = _create_syllabus_and_calendar(client)

        client.post("/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id})
        client.post("/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id})

        resp = client.get(f"/api/allocation/{syllabus_id}/{calendar_id}")
        assert resp.status_code == 200
        total_periods = sum(a["periods"] for a in resp.json()["assignments"])
        # With budget=5 and planned_periods=5, should be exactly 5
        assert total_periods == 5


class TestLessonPlanDateDerivation:
    """Tests for fix #2: multi-period-per-day date derivation."""

    def test_multi_period_day_dates(self, client):
        """With 7 periods in 5 days, periods 1-2 should share Monday, etc."""
        # 7 periods per week across 5 days = ceil(7/5)=2 periods/day
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
                            "planned_periods": 7,
                            "objectives": [
                                {"order": 1, "text": "Count natural numbers"},
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
                            "period_budget": 7,
                            "label": "Week 1",
                        },
                    ],
                },
            ],
        }

        syl_resp = client.post("/api/syllabus", json=syllabus_data)
        syllabus_id = syl_resp.json()["id"]
        cal_resp = client.post("/api/calendar", json=calendar_data)
        calendar_id = cal_resp.json()["id"]

        client.post("/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id})

        resp = client.get(f"/api/lesson-plan/{syllabus_id}/{calendar_id}/week/1")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data) == 7

        # With 7 periods and 5 days: periods_per_day = ceil(7/5) = 2
        # period 1 -> day_offset = (1-1)//2 = 0 -> 2026-01-05 (Monday)
        # period 2 -> day_offset = (2-1)//2 = 0 -> 2026-01-05 (Monday)
        # period 3 -> day_offset = (3-1)//2 = 1 -> 2026-01-06 (Tuesday)
        # period 4 -> day_offset = (4-1)//2 = 1 -> 2026-01-06 (Tuesday)
        # period 5 -> day_offset = (5-1)//2 = 2 -> 2026-01-07 (Wednesday)
        # period 6 -> day_offset = (6-1)//2 = 2 -> 2026-01-07 (Wednesday)
        # period 7 -> day_offset = (7-1)//2 = 3 -> 2026-01-08 (Thursday)
        dates = [plan["date"] for plan in data]
        assert dates[0] == "2026-01-05"  # period 1 Monday
        assert dates[1] == "2026-01-05"  # period 2 Monday
        assert dates[2] == "2026-01-06"  # period 3 Tuesday
        assert dates[3] == "2026-01-06"  # period 4 Tuesday
        assert dates[4] == "2026-01-07"  # period 5 Wednesday
        assert dates[5] == "2026-01-07"  # period 6 Wednesday
        assert dates[6] == "2026-01-08"  # period 7 Thursday

    def test_five_periods_five_days_still_works(self, client):
        """With 5 periods in 5 days (1 per day), each period gets its own day."""
        syllabus_id, calendar_id = _create_syllabus_and_calendar(client, period_budget=5)

        client.post("/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id})

        resp = client.get(f"/api/lesson-plan/{syllabus_id}/{calendar_id}/week/1")
        assert resp.status_code == 200
        data = resp.json()

        dates = [plan["date"] for plan in data]
        assert dates == [
            "2026-01-05",
            "2026-01-06",
            "2026-01-07",
            "2026-01-08",
            "2026-01-09",
        ]


class TestSchemeTeachingMethods:
    """Tests for fix #3: teaching methods derived from competences."""

    def test_scheme_uses_competences_for_methods(self, client):
        """Scheme teaching_methods should vary based on sub-topic competences."""
        syllabus_id, calendar_id = _create_syllabus_and_calendar(client)

        client.post("/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id})

        resp = client.get(f"/api/scheme/{syllabus_id}/{calendar_id}")
        assert resp.status_code == 200
        data = resp.json()

        entry = data["entries"][0]
        # Should contain "Explanation" as base and derived methods
        assert "Explanation" in entry["teaching_methods"]
        # Should NOT be the old hardcoded value
        assert entry["teaching_methods"] != "Presentations, Problem solving, Practical work, Research, Group discussion"

    def test_scheme_references_not_hardcoded(self, client):
        """Scheme references should be data-driven (not TIE hardcoded string)."""
        syllabus_id, calendar_id = _create_syllabus_and_calendar(client)

        client.post("/api/allocate", json={"syllabus_id": syllabus_id, "calendar_id": calendar_id})

        resp = client.get(f"/api/scheme/{syllabus_id}/{calendar_id}")
        assert resp.status_code == 200
        data = resp.json()

        entry = data["entries"][0]
        # Should NOT contain the old hardcoded reference
        assert entry["references"] != "TIE(2023), Basic Mathematics for Secondary Schools Book 1, TIE-DSM"
        # Should have a sensible default
        assert entry["references"] is not None


class TestTextbookFKValidation:
    """Tests for fix #4: FK validation on textbook POST."""

    def test_textbook_rejects_invalid_sub_topic_id(self, client):
        """POST /api/textbook with non-existent sub_topic_id should return 422."""
        textbook_payload = [
            {
                "sub_topic_id": 99999,
                "book_title": "Nonexistent Book",
                "start_page": 1,
                "end_page": 10,
            },
        ]

        response = client.post("/api/textbook/", json=textbook_payload)
        assert response.status_code == 422
        assert "does not exist" in response.json()["detail"]

    def test_textbook_accepts_valid_sub_topic_id(self, client):
        """POST /api/textbook with valid sub_topic_id should succeed."""
        syllabus_payload = {
            "subject": "Mathematics",
            "form": "Form 1",
            "topics": [
                {
                    "order": 1,
                    "topic_id_code": "1.0",
                    "title": "Numbers",
                    "sub_topics": [
                        {
                            "order": 1,
                            "sub_topic_id_code": "1.1",
                            "title": "Natural Numbers",
                            "planned_periods": 6,
                            "objectives": [],
                        },
                    ],
                }
            ],
        }
        syl_resp = client.post("/api/syllabus/", json=syllabus_payload)
        sub_topic_id = syl_resp.json()["topics"][0]["sub_topics"][0]["id"]

        textbook_payload = [
            {
                "sub_topic_id": sub_topic_id,
                "book_title": "Test Book",
                "start_page": 1,
                "end_page": 10,
            },
        ]

        response = client.post("/api/textbook/", json=textbook_payload)
        assert response.status_code == 201
