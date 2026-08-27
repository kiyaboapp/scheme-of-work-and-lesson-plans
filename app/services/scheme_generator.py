"""Scheme of work generator: produces the full weekly plan from allocation data."""

from sqlalchemy.orm import Session

from app.models import (
    AllocationAssignment,
    CalendarData,
    Syllabus,
    SubTopic,
    Term,
    TextbookEntry,
    Topic,
    Week,
)
from app.schemas import SchemeOfWorkEntry, SchemeOfWorkResponse


def generate_scheme_of_work(
    syllabus_id: int, calendar_id: int, db: Session
) -> SchemeOfWorkResponse:
    """
    Generate a complete scheme of work from stored allocation assignments.

    Loads assignments ordered by week_number and slot, then builds
    SchemeOfWorkEntry objects with all relevant details.
    """
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise ValueError(f"Syllabus with id {syllabus_id} not found")

    calendar = db.query(CalendarData).filter(CalendarData.id == calendar_id).first()
    if not calendar:
        raise ValueError(f"Calendar with id {calendar_id} not found")

    # Load assignments ordered by week_number and slot
    assignments = (
        db.query(AllocationAssignment)
        .join(Week, AllocationAssignment.week_id == Week.id)
        .join(Term, Week.term_id == Term.id)
        .filter(
            AllocationAssignment.syllabus_id == syllabus_id,
            AllocationAssignment.calendar_id == calendar_id,
        )
        .order_by(Term.order, Week.week_number, AllocationAssignment.slot)
        .all()
    )

    entries: list[SchemeOfWorkEntry] = []

    for assignment in assignments:
        week = assignment.week
        term = week.term
        sub_topic = assignment.sub_topic
        topic = sub_topic.topic

        # Build sub-topic title with split info
        sub_topic_title = sub_topic.title
        if assignment.split_total and assignment.split_total > 1:
            sub_topic_title += f" (Part {assignment.split_index}/{assignment.split_total})"

        # Get objectives ordered by order
        objectives = sorted(sub_topic.objectives, key=lambda o: o.order)
        objective_texts = [obj.text for obj in objectives]

        # Get textbook references for this sub-topic
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
            teaching_resources = "Charts, real objects"

        entry = SchemeOfWorkEntry(
            week_number=week.week_number,
            week_label=week.label,
            term=term.title,
            topic_title=topic.title,
            sub_topic_title=sub_topic_title,
            objectives=objective_texts,
            periods=assignment.periods,
            teaching_methods="Presentations, Problem solving, Practical work, Research, Group discussion",
            teaching_resources=teaching_resources,
            references="TIE(2023), Basic Mathematics for Secondary Schools Book 1, TIE-DSM",
        )
        entries.append(entry)

    return SchemeOfWorkResponse(
        syllabus_id=syllabus_id,
        calendar_id=calendar_id,
        subject=syllabus.subject,
        form=syllabus.form,
        academic_year=calendar.academic_year,
        entries=entries,
    )
