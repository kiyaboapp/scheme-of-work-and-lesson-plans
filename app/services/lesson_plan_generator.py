"""Lesson plan generator: produces per-period lesson plans from allocation data."""

import math
from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    AllocationAssignment,
    LessonPlan,
    Term,
    TextbookEntry,
    Week,
)

# Number of school days in a week (Monday to Friday)
SCHOOL_DAYS_PER_WEEK = 5


def generate_lesson_plans_for_week(
    syllabus_id: int,
    calendar_id: int,
    week_number: int,
    db: Session,
    period_number: Optional[int] = None,
) -> list[LessonPlan]:
    """
    Generate lesson plans for a given week (or a specific period within it).

    If period_number is None, generates plans for all periods assigned in that week.
    If period_number is provided, generates only for that specific period.
    """
    # Find the week
    week = (
        db.query(Week)
        .join(Term)
        .filter(
            Term.calendar_id == calendar_id,
            Week.week_number == week_number,
        )
        .first()
    )

    if not week:
        return []

    # Find assignments for this week
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

    if not assignments:
        return []

    lesson_plans: list[LessonPlan] = []

    # Calculate periods per day for this week (for date derivation)
    week_budget = week.period_budget or 0
    periods_per_day = max(1, math.ceil(week_budget / SCHOOL_DAYS_PER_WEEK))

    for assignment in assignments:
        sub_topic = assignment.sub_topic
        objectives = sorted(sub_topic.objectives, key=lambda o: o.order)
        first_objective_text = objectives[0].text if objectives else sub_topic.title

        # Determine textbook resources
        textbook_entries = (
            db.query(TextbookEntry)
            .filter(TextbookEntry.sub_topic_id == sub_topic.id)
            .all()
        )
        if textbook_entries:
            resources_parts = []
            for entry in textbook_entries:
                ref = entry.book_title
                if entry.start_page and entry.end_page:
                    ref += f" pp.{entry.start_page}-{entry.end_page}"
                elif entry.start_page:
                    ref += f" p.{entry.start_page}"
                resources_parts.append(ref)
            teaching_resources = ", ".join(resources_parts)
        else:
            teaching_resources = "Charts, calculators, real objects"

        # Generate lesson plans for each period in this assignment
        for p in range(assignment.first_period, assignment.last_period + 1):
            if period_number is not None and p != period_number:
                continue

            # Check if lesson plan already exists
            existing = (
                db.query(LessonPlan)
                .filter(
                    LessonPlan.assignment_id == assignment.id,
                    LessonPlan.period_number == p,
                )
                .first()
            )

            if existing:
                lesson_plans.append(existing)
                continue

            # Calculate date from week start_date using periods_per_day
            plan_date = None
            if week.start_date:
                day_offset = (p - 1) // periods_per_day
                plan_date = week.start_date + timedelta(days=day_offset)

            lesson_plan = LessonPlan(
                assignment_id=assignment.id,
                period_number=p,
                date=plan_date,
                teacher_activities=(
                    f"Guide students to {first_objective_text}. "
                    "Demonstrate using examples. Provide exercises."
                ),
                student_activities=(
                    "Participate in discussion. Practice solving problems. "
                    "Present results to class."
                ),
                assessment="Oral questions, exercises, quizzes, homework",
                consolidation=f"Review key concepts. Assign homework on {sub_topic.title}.",
                teaching_resources=teaching_resources,
                remarks=None,
            )
            db.add(lesson_plan)
            lesson_plans.append(lesson_plan)

    db.commit()
    for lp in lesson_plans:
        db.refresh(lp)

    return lesson_plans
