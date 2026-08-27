"""Textbook entry ingestion API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SubTopic, TextbookEntry
from app.schemas import TextbookEntryInput, TextbookEntryResponse

router = APIRouter(prefix="/api/textbook", tags=["textbook"])


@router.post(
    "/",
    response_model=list[TextbookEntryResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_textbook_entries(
    payload: list[TextbookEntryInput], db: Session = Depends(get_db)
):
    """Create textbook entries linking sub-topics to textbook page ranges."""
    entries = []
    for entry_input in payload:
        # Validate that the referenced sub_topic exists
        sub_topic = db.query(SubTopic).filter(SubTopic.id == entry_input.sub_topic_id).first()
        if not sub_topic:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"SubTopic with id {entry_input.sub_topic_id} does not exist",
            )

        entry = TextbookEntry(
            sub_topic_id=entry_input.sub_topic_id,
            book_title=entry_input.book_title,
            start_page=entry_input.start_page,
            end_page=entry_input.end_page,
            note=entry_input.note,
        )
        db.add(entry)
        entries.append(entry)

    db.commit()
    for entry in entries:
        db.refresh(entry)
    return entries


@router.get("/", response_model=list[TextbookEntryResponse])
def list_textbook_entries(db: Session = Depends(get_db)):
    """List all textbook entries."""
    return db.query(TextbookEntry).all()
