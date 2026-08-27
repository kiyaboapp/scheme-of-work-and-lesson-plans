"""Lesson plan router: endpoints for generating and retrieving lesson plans."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import LessonPlanResponse
from app.services.lesson_plan_generator import generate_lesson_plans_for_week

router = APIRouter(prefix="/api", tags=["lesson-plan"])


@router.get(
    "/lesson-plan/{syllabus_id}/{calendar_id}/week/{week_number}",
    response_model=list[LessonPlanResponse],
)
def get_lesson_plans_for_week(
    syllabus_id: int, calendar_id: int, week_number: int, db: Session = Depends(get_db)
):
    """Return all lesson plans for a given week (generates if not existing)."""
    plans = generate_lesson_plans_for_week(syllabus_id, calendar_id, week_number, db)
    if not plans:
        raise HTTPException(
            status_code=404,
            detail=f"No assignments found for week {week_number}. "
            f"Valid weeks are those with teaching classification that have allocations.",
        )
    return [LessonPlanResponse.model_validate(p) for p in plans]


@router.get(
    "/lesson-plan/{syllabus_id}/{calendar_id}/week/{week_number}/period/{period_number}",
    response_model=LessonPlanResponse,
)
def get_lesson_plan_for_period(
    syllabus_id: int,
    calendar_id: int,
    week_number: int,
    period_number: int,
    db: Session = Depends(get_db),
):
    """Return a single lesson plan for a specific week and period."""
    plans = generate_lesson_plans_for_week(
        syllabus_id, calendar_id, week_number, db, period_number=period_number
    )
    if not plans:
        raise HTTPException(
            status_code=404,
            detail=f"No lesson plan found for week {week_number}, period {period_number}.",
        )
    return LessonPlanResponse.model_validate(plans[0])
