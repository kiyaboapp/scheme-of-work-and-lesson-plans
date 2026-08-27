"""Allocation engine: greedy sequential bin-packing of sub-topics into teaching weeks."""

from sqlalchemy.orm import Session

from app.models import (
    AllocationAssignment,
    CalendarData,
    SubTopic,
    Syllabus,
    Term,
    Topic,
    Week,
    WeekClassification,
)


def run_allocation(syllabus_id: int, calendar_id: int, db: Session) -> list[AllocationAssignment]:
    """
    Run the greedy sequential bin-packing algorithm.

    Iterates sub-topics in syllabus order (topic.order, sub_topic.order).
    For each sub-topic, assigns its planned_periods to teaching weeks
    respecting period_budget. Splits across weeks when needed.
    """
    # Load syllabus with topics and sub-topics in order
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise ValueError(f"Syllabus with id {syllabus_id} not found")

    calendar = db.query(CalendarData).filter(CalendarData.id == calendar_id).first()
    if not calendar:
        raise ValueError(f"Calendar with id {calendar_id} not found")

    # Get ordered sub-topics from syllabus
    sub_topics = (
        db.query(SubTopic)
        .join(Topic)
        .filter(Topic.syllabus_id == syllabus_id)
        .order_by(Topic.order, SubTopic.order)
        .all()
    )

    # Get teaching weeks ordered by term order and week number
    teaching_weeks = (
        db.query(Week)
        .join(Term)
        .filter(
            Term.calendar_id == calendar_id,
            Week.classification == WeekClassification.teaching,
            Week.period_budget > 0,
        )
        .order_by(Term.order, Week.week_number)
        .all()
    )

    if not teaching_weeks:
        return []

    # Track capacity used per week
    week_capacity_used: dict[int, int] = {w.id: 0 for w in teaching_weeks}
    week_slot_counter: dict[int, int] = {w.id: 0 for w in teaching_weeks}

    all_assignments: list[AllocationAssignment] = []
    week_index = 0

    for sub_topic in sub_topics:
        remaining = sub_topic.planned_periods
        if remaining <= 0:
            continue

        parts: list[AllocationAssignment] = []
        split_index = 1

        while remaining > 0 and week_index < len(teaching_weeks):
            week = teaching_weeks[week_index]
            budget = week.period_budget or 0
            available = budget - week_capacity_used[week.id]

            if available <= 0:
                week_index += 1
                continue

            take = min(remaining, available)

            # Calculate first/last period within the week
            first_period = week_capacity_used[week.id] + 1
            last_period = week_capacity_used[week.id] + take

            # Increment slot counter for this week
            week_slot_counter[week.id] += 1
            slot = week_slot_counter[week.id]

            assignment = AllocationAssignment(
                syllabus_id=syllabus_id,
                calendar_id=calendar_id,
                week_id=week.id,
                sub_topic_id=sub_topic.id,
                slot=slot,
                first_period=first_period,
                last_period=last_period,
                periods=take,
                split_index=split_index,
                split_total=1,  # Placeholder, updated after loop
            )
            parts.append(assignment)
            all_assignments.append(assignment)

            week_capacity_used[week.id] += take
            remaining -= take
            split_index += 1

            # Move to next week if current is full
            if week_capacity_used[week.id] >= budget:
                week_index += 1

        # Update split_total for all parts of this sub-topic
        total_parts = len(parts)
        for part in parts:
            part.split_total = total_parts

    # Store all assignments in DB
    db.add_all(all_assignments)
    db.commit()

    # Refresh to get IDs
    for assignment in all_assignments:
        db.refresh(assignment)

    return all_assignments
