"""Tests for textbook entry ingestion API endpoints."""


def test_create_textbook_entries_returns_201(client):
    """POST /api/textbook with valid JSON stores entries and returns 201."""
    # First, create a syllabus with sub-topics so we have valid sub_topic IDs
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
                    {
                        "order": 2,
                        "sub_topic_id_code": "1.2",
                        "title": "Integers",
                        "planned_periods": 4,
                        "objectives": [],
                    },
                ],
            }
        ],
    }
    syllabus_response = client.post("/api/syllabus/", json=syllabus_payload)
    assert syllabus_response.status_code == 201
    syllabus_data = syllabus_response.json()
    sub_topic_1_id = syllabus_data["topics"][0]["sub_topics"][0]["id"]
    sub_topic_2_id = syllabus_data["topics"][0]["sub_topics"][1]["id"]

    # Create textbook entries
    textbook_payload = [
        {
            "sub_topic_id": sub_topic_1_id,
            "book_title": "Mathematics Form 1 - WazaElimu",
            "start_page": 1,
            "end_page": 15,
            "note": "Chapter 1: Natural Numbers",
        },
        {
            "sub_topic_id": sub_topic_2_id,
            "book_title": "Mathematics Form 1 - WazaElimu",
            "start_page": 16,
            "end_page": 28,
            "note": None,
        },
    ]

    response = client.post("/api/textbook/", json=textbook_payload)
    assert response.status_code == 201

    data = response.json()
    assert len(data) == 2
    assert data[0]["book_title"] == "Mathematics Form 1 - WazaElimu"
    assert data[0]["start_page"] == 1
    assert data[0]["end_page"] == 15
    assert data[0]["note"] == "Chapter 1: Natural Numbers"
    assert data[0]["id"] is not None
    assert data[1]["sub_topic_id"] == sub_topic_2_id


def test_list_textbook_entries(client):
    """GET /api/textbook lists all textbook entries."""
    # Create a syllabus first
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
    syllabus_response = client.post("/api/syllabus/", json=syllabus_payload)
    sub_topic_id = syllabus_response.json()["topics"][0]["sub_topics"][0]["id"]

    # Create textbook entries
    textbook_payload = [
        {
            "sub_topic_id": sub_topic_id,
            "book_title": "Mathematics Form 1",
            "start_page": 1,
            "end_page": 10,
        },
    ]
    client.post("/api/textbook/", json=textbook_payload)

    # List all entries
    response = client.get("/api/textbook/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["book_title"] == "Mathematics Form 1"
    assert data[0]["sub_topic_id"] == sub_topic_id


def test_create_empty_textbook_entries(client):
    """POST /api/textbook with empty list returns 201 with empty result."""
    response = client.post("/api/textbook/", json=[])
    assert response.status_code == 201
    assert response.json() == []
