"""Smoke tests to verify the application starts and tables are created."""

from sqlalchemy import inspect

from app.database import Base
from app.models import (
    AllocationAssignment,
    CalendarData,
    LessonPlan,
    Objective,
    SubTopic,
    Syllabus,
    Term,
    TextbookEntry,
    Topic,
    Week,
)


def test_app_health_endpoint(client):
    """Test that the health check endpoint responds correctly."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_app_title(client):
    """Test that the application has the correct title."""
    from app.main import app

    assert app.title == "SOW Generator"


def test_all_tables_created(db_session):
    """Test that all expected tables are created in the database."""
    inspector = inspect(db_session.bind)
    table_names = inspector.get_table_names()

    expected_tables = [
        "syllabuses",
        "topics",
        "sub_topics",
        "objectives",
        "calendar_data",
        "terms",
        "weeks",
        "textbook_entries",
        "allocation_assignments",
        "lesson_plans",
    ]

    for table in expected_tables:
        assert table in table_names, f"Table '{table}' not found in database"


def test_models_importable():
    """Test that all models can be imported without errors."""
    assert Syllabus.__tablename__ == "syllabuses"
    assert Topic.__tablename__ == "topics"
    assert SubTopic.__tablename__ == "sub_topics"
    assert Objective.__tablename__ == "objectives"
    assert CalendarData.__tablename__ == "calendar_data"
    assert Term.__tablename__ == "terms"
    assert Week.__tablename__ == "weeks"
    assert TextbookEntry.__tablename__ == "textbook_entries"
    assert AllocationAssignment.__tablename__ == "allocation_assignments"
    assert LessonPlan.__tablename__ == "lesson_plans"


def test_create_syllabus(db_session):
    """Test creating a syllabus record in the database."""
    syllabus = Syllabus(subject="Mathematics", form="Form 1", source_note="Test")
    db_session.add(syllabus)
    db_session.commit()
    db_session.refresh(syllabus)

    assert syllabus.id is not None
    assert syllabus.subject == "Mathematics"
    assert syllabus.form == "Form 1"


def test_create_topic_with_subtopics(db_session):
    """Test creating a topic with nested sub-topics and objectives."""
    syllabus = Syllabus(subject="Mathematics", form="Form 1")
    db_session.add(syllabus)
    db_session.commit()

    topic = Topic(
        syllabus_id=syllabus.id,
        order=1,
        topic_id_code="1.0",
        title="Numbers",
    )
    db_session.add(topic)
    db_session.commit()

    sub_topic = SubTopic(
        topic_id=topic.id,
        order=1,
        sub_topic_id_code="1.1",
        title="Natural Numbers",
        planned_periods=6,
        competences=["counting", "operations"],
    )
    db_session.add(sub_topic)
    db_session.commit()

    objective = Objective(
        sub_topic_id=sub_topic.id,
        order=1,
        text="Students should be able to count natural numbers",
    )
    db_session.add(objective)
    db_session.commit()

    # Verify relationships
    db_session.refresh(syllabus)
    assert len(syllabus.topics) == 1
    assert len(syllabus.topics[0].sub_topics) == 1
    assert len(syllabus.topics[0].sub_topics[0].objectives) == 1
    assert syllabus.topics[0].sub_topics[0].competences == ["counting", "operations"]
