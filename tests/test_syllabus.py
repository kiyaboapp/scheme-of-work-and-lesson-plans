"""Tests for syllabus ingestion API endpoints."""


VALID_SYLLABUS_PAYLOAD = {
    "subject": "Mathematics",
    "form": "Form 1",
    "source_note": "Tanzania O-Level Syllabus 2024",
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
                    "competences": ["counting", "operations"],
                    "objectives": [
                        {"order": 1, "text": "Count natural numbers up to billions"},
                        {"order": 2, "text": "Perform operations on natural numbers"},
                    ],
                },
                {
                    "order": 2,
                    "sub_topic_id_code": "1.2",
                    "title": "Integers",
                    "planned_periods": 4,
                    "competences": None,
                    "objectives": [
                        {"order": 1, "text": "Define integers"},
                    ],
                },
            ],
        },
        {
            "order": 2,
            "topic_id_code": "2.0",
            "title": "Fractions",
            "sub_topics": [
                {
                    "order": 1,
                    "sub_topic_id_code": "2.1",
                    "title": "Proper Fractions",
                    "planned_periods": 5,
                    "objectives": [
                        {"order": 1, "text": "Simplify fractions"},
                    ],
                },
            ],
        },
    ],
}


def test_create_syllabus_returns_201(client):
    """POST /api/syllabus with valid JSON stores data and returns 201."""
    response = client.post("/api/syllabus/", json=VALID_SYLLABUS_PAYLOAD)
    assert response.status_code == 201

    data = response.json()
    assert data["subject"] == "Mathematics"
    assert data["form"] == "Form 1"
    assert data["source_note"] == "Tanzania O-Level Syllabus 2024"
    assert data["id"] is not None
    assert "created_at" in data

    # Verify nested topics
    assert len(data["topics"]) == 2
    topic1 = data["topics"][0]
    assert topic1["topic_id_code"] == "1.0"
    assert topic1["title"] == "Numbers"
    assert len(topic1["sub_topics"]) == 2

    # Verify nested sub-topics
    st1 = topic1["sub_topics"][0]
    assert st1["sub_topic_id_code"] == "1.1"
    assert st1["title"] == "Natural Numbers"
    assert st1["planned_periods"] == 6
    assert st1["competences"] == ["counting", "operations"]
    assert len(st1["objectives"]) == 2

    # Verify objectives
    obj1 = st1["objectives"][0]
    assert obj1["order"] == 1
    assert obj1["text"] == "Count natural numbers up to billions"


def test_get_syllabus_by_id_returns_nested_structure(client):
    """GET /api/syllabus/{id} returns the complete nested structure."""
    # Create a syllabus first
    create_response = client.post("/api/syllabus/", json=VALID_SYLLABUS_PAYLOAD)
    assert create_response.status_code == 201
    syllabus_id = create_response.json()["id"]

    # Retrieve it by ID
    response = client.get(f"/api/syllabus/{syllabus_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == syllabus_id
    assert data["subject"] == "Mathematics"
    assert len(data["topics"]) == 2

    # Verify full depth: syllabus > topics > sub_topics > objectives
    topic = data["topics"][0]
    assert len(topic["sub_topics"]) == 2
    sub_topic = topic["sub_topics"][0]
    assert len(sub_topic["objectives"]) == 2
    assert sub_topic["objectives"][0]["text"] == "Count natural numbers up to billions"


def test_get_syllabus_not_found(client):
    """GET /api/syllabus/{id} returns 404 for non-existent ID."""
    response = client.get("/api/syllabus/9999")
    assert response.status_code == 404


def test_list_syllabuses(client):
    """GET /api/syllabus lists all syllabuses."""
    # Create two syllabuses
    client.post("/api/syllabus/", json=VALID_SYLLABUS_PAYLOAD)
    client.post(
        "/api/syllabus/",
        json={"subject": "Physics", "form": "Form 2", "topics": []},
    )

    response = client.get("/api/syllabus/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    subjects = [s["subject"] for s in data]
    assert "Mathematics" in subjects
    assert "Physics" in subjects


def test_create_syllabus_missing_required_fields(client):
    """POST /api/syllabus with missing required fields returns 422."""
    # Missing 'form' field
    response = client.post("/api/syllabus/", json={"subject": "Mathematics"})
    assert response.status_code == 422

    # Empty body
    response = client.post("/api/syllabus/", json={})
    assert response.status_code == 422


def test_create_syllabus_missing_sub_topic_fields(client):
    """POST /api/syllabus with missing sub-topic required fields returns 422."""
    payload = {
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
                        # Missing sub_topic_id_code and title
                        "planned_periods": 6,
                    }
                ],
            }
        ],
    }
    response = client.post("/api/syllabus/", json=payload)
    assert response.status_code == 422
