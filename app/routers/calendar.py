"""Calendar ingestion API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CalendarData, Term, Week, WeekClassification
from app.schemas import CalendarInput, CalendarResponse

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.post("/", response_model=CalendarResponse, status_code=status.HTTP_201_CREATED)
def create_calendar(payload: CalendarInput, db: Session = Depends(get_db)):
    """Create a calendar with all nested terms and weeks."""
    calendar = CalendarData(academic_year=payload.academic_year)
    db.add(calendar)
    db.flush()

    for term_input in payload.terms:
        term = Term(
            calendar_id=calendar.id,
            order=term_input.order,
            term_id_code=term_input.term_id_code,
            title=term_input.title,
        )
        db.add(term)
        db.flush()

        for week_input in term_input.weeks:
            week = Week(
                term_id=term.id,
                week_number=week_input.week_number,
                start_date=week_input.start_date,
                end_date=week_input.end_date,
                classification=WeekClassification(week_input.classification),
                period_budget=week_input.period_budget,
                label=week_input.label,
            )
            db.add(week)

    db.commit()
    db.refresh(calendar)
    return calendar


@router.get("/", response_model=list[CalendarResponse])
def list_calendars(db: Session = Depends(get_db)):
    """List all calendars (with nested data)."""
    calendars = db.query(CalendarData).all()
    return calendars


@router.get("/{calendar_id}", response_model=CalendarResponse)
def get_calendar(calendar_id: int, db: Session = Depends(get_db)):
    """Get a single calendar with all nested terms and weeks."""
    calendar = db.query(CalendarData).filter(CalendarData.id == calendar_id).first()
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calendar with id {calendar_id} not found",
        )
    return calendar
