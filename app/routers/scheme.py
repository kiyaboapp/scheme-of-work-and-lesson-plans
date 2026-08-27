"""Scheme of work router: endpoint for generating and retrieving the full scheme."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SchemeOfWorkResponse
from app.services.docx_scheme_writer import generate_scheme_docx
from app.services.scheme_generator import generate_scheme_of_work

router = APIRouter(prefix="/api", tags=["scheme"])

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


@router.get("/scheme/{syllabus_id}/{calendar_id}", response_model=SchemeOfWorkResponse)
def get_scheme(syllabus_id: int, calendar_id: int, db: Session = Depends(get_db)):
    """Generate and return the complete scheme of work."""
    try:
        scheme = generate_scheme_of_work(syllabus_id, calendar_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return scheme


@router.get("/scheme/{syllabus_id}/{calendar_id}/docx")
def get_scheme_docx(syllabus_id: int, calendar_id: int, db: Session = Depends(get_db)):
    """Generate and return the scheme of work as a .docx file."""
    try:
        scheme = generate_scheme_of_work(syllabus_id, calendar_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    docx_bytes = generate_scheme_docx(scheme)

    filename = (
        f"Scheme_of_Work_{scheme.subject}_{scheme.form}_{scheme.academic_year}.docx"
    )
    filename = filename.replace(" ", "_")

    return StreamingResponse(
        docx_bytes,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
