"""Allocation router: endpoints for running and querying the allocation engine."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AllocationAssignment
from app.schemas import AllocationAssignmentResponse, AllocationResponse
from app.services.allocation import run_allocation

router = APIRouter(prefix="/api", tags=["allocation"])


class AllocateRequest(BaseModel):
    """Request body for the allocate endpoint."""

    syllabus_id: int
    calendar_id: int


@router.post("/allocate", response_model=AllocationResponse)
def allocate(request: AllocateRequest, db: Session = Depends(get_db)):
    """Run the allocation engine for a given syllabus and calendar."""
    try:
        assignments = run_allocation(request.syllabus_id, request.calendar_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return AllocationResponse(
        syllabus_id=request.syllabus_id,
        calendar_id=request.calendar_id,
        assignments=[AllocationAssignmentResponse.model_validate(a) for a in assignments],
    )


@router.get("/allocation/{syllabus_id}/{calendar_id}", response_model=AllocationResponse)
def get_allocation(syllabus_id: int, calendar_id: int, db: Session = Depends(get_db)):
    """Retrieve existing allocation assignments for a syllabus/calendar pair."""
    assignments = (
        db.query(AllocationAssignment)
        .filter(
            AllocationAssignment.syllabus_id == syllabus_id,
            AllocationAssignment.calendar_id == calendar_id,
        )
        .order_by(AllocationAssignment.id)
        .all()
    )

    return AllocationResponse(
        syllabus_id=syllabus_id,
        calendar_id=calendar_id,
        assignments=[AllocationAssignmentResponse.model_validate(a) for a in assignments],
    )
