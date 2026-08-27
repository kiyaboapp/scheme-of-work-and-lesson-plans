"""Syllabus ingestion API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Objective, SubTopic, Syllabus, Topic
from app.schemas import SyllabusInput, SyllabusResponse

router = APIRouter(prefix="/api/syllabus", tags=["syllabus"])


@router.post("/", response_model=SyllabusResponse, status_code=status.HTTP_201_CREATED)
def create_syllabus(payload: SyllabusInput, db: Session = Depends(get_db)):
    """Create a syllabus with all nested topics, sub-topics, and objectives."""
    syllabus = Syllabus(
        subject=payload.subject,
        form=payload.form,
        source_note=payload.source_note,
    )
    db.add(syllabus)
    db.flush()

    for topic_input in payload.topics:
        topic = Topic(
            syllabus_id=syllabus.id,
            order=topic_input.order,
            topic_id_code=topic_input.topic_id_code,
            title=topic_input.title,
        )
        db.add(topic)
        db.flush()

        for sub_topic_input in topic_input.sub_topics:
            sub_topic = SubTopic(
                topic_id=topic.id,
                order=sub_topic_input.order,
                sub_topic_id_code=sub_topic_input.sub_topic_id_code,
                title=sub_topic_input.title,
                planned_periods=sub_topic_input.planned_periods,
                competences=sub_topic_input.competences,
            )
            db.add(sub_topic)
            db.flush()

            for obj_input in sub_topic_input.objectives:
                objective = Objective(
                    sub_topic_id=sub_topic.id,
                    order=obj_input.order,
                    text=obj_input.text,
                )
                db.add(objective)

    db.commit()
    db.refresh(syllabus)
    return syllabus


@router.get("/", response_model=list[SyllabusResponse])
def list_syllabuses(db: Session = Depends(get_db)):
    """List all syllabuses (with nested data)."""
    syllabuses = db.query(Syllabus).all()
    return syllabuses


@router.get("/{syllabus_id}", response_model=SyllabusResponse)
def get_syllabus(syllabus_id: int, db: Session = Depends(get_db)):
    """Get a single syllabus with all nested topics, sub-topics, and objectives."""
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus with id {syllabus_id} not found",
        )
    return syllabus
