"""Scheme of work router: endpoint for generating and retrieving the full scheme."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SchemeOfWorkResponse
from app.services.scheme_generator import generate_scheme_of_work

router = APIRouter(prefix="/api", tags=["scheme"])


@router.get("/scheme/{syllabus_id}/{calendar_id}", response_model=SchemeOfWorkResponse)
def get_scheme(syllabus_id: int, calendar_id: int, db: Session = Depends(get_db)):
    """Generate and return the complete scheme of work."""
    try:
        scheme = generate_scheme_of_work(syllabus_id, calendar_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return scheme
