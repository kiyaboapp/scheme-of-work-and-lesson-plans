"""Lesson plan router: endpoints for generating and retrieving lesson plans."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AllocationAssignment, LessonPlan, Syllabus, Term, Week
from app.schemas import LessonPlanResponse
from app.services.docx_lesson_plan_writer import generate_lesson_plan_docx
from app.services.lesson_plan_generator import generate_lesson_plans_for_week

router = APIRouter(prefix="/api", tags=["lesson-plan"])

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


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


@router.get("/lesson-plan/{syllabus_id}/{calendar_id}/docx")
def get_lesson_plans_docx(
    syllabus_id: int, calendar_id: int, db: Session = Depends(get_db)
):
    """Generate all lesson plans for the syllabus/calendar pair and return as .docx."""
    # Verify syllabus exists
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail=f"Syllabus {syllabus_id} not found")

    # Get all teaching weeks for this calendar that have allocations
    teaching_weeks = (
        db.query(Week)
        .join(Term)
        .filter(
            Term.calendar_id == calendar_id,
            Week.classification == "teaching",
        )
        .order_by(Term.order, Week.week_number)
        .all()
    )

    if not teaching_weeks:
        raise HTTPException(
            status_code=404,
            detail="No teaching weeks found for this calendar.",
        )

    # Generate lesson plans for each week
    all_assignments = []
    lesson_plans_by_assignment: dict[int, list[LessonPlan]] = {}

    for week in teaching_weeks:
        plans = generate_lesson_plans_for_week(
            syllabus_id, calendar_id, week.week_number, db
        )
        if plans:
            # Get assignments for this week
            assignments = (
                db.query(AllocationAssignment)
                .filter(
                    AllocationAssignment.syllabus_id == syllabus_id,
                    AllocationAssignment.calendar_id == calendar_id,
                    AllocationAssignment.week_id == week.id,
                )
                .order_by(AllocationAssignment.slot)
                .all()
            )
            for assignment in assignments:
                if assignment not in all_assignments:
                    all_assignments.append(assignment)
                    # Get lesson plans for this assignment
                    assignment_plans = [
                        p for p in plans if p.assignment_id == assignment.id
                    ]
                    lesson_plans_by_assignment[assignment.id] = assignment_plans

    if not all_assignments:
        raise HTTPException(
            status_code=404,
            detail="No lesson plans could be generated. "
            "Ensure allocation has been run for this syllabus/calendar.",
        )

    docx_bytes = generate_lesson_plan_docx(
        assignments=all_assignments,
        lesson_plans_by_assignment=lesson_plans_by_assignment,
        subject=syllabus.subject,
        form=syllabus.form,
    )

    filename = f"Lesson_Plans_{syllabus.subject}_{syllabus.form}.docx".replace(" ", "_")

    return StreamingResponse(
        docx_bytes,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
