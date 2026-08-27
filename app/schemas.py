"""Pydantic schemas for API request/response validation."""

import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ==================== Input Schemas ====================


class ObjectiveInput(BaseModel):
    """Input schema for a learning objective."""

    order: int
    text: str


class SubTopicInput(BaseModel):
    """Input schema for a sub-topic."""

    order: int
    sub_topic_id_code: str
    title: str
    planned_periods: int
    competences: Optional[list[str]] = None
    objectives: list[ObjectiveInput] = []


class TopicInput(BaseModel):
    """Input schema for a topic."""

    order: int
    topic_id_code: str
    title: str
    sub_topics: list[SubTopicInput] = []


class SyllabusInput(BaseModel):
    """Input schema for creating/uploading a syllabus."""

    subject: str
    form: str
    source_note: Optional[str] = None
    topics: list[TopicInput] = []


class WeekInput(BaseModel):
    """Input schema for a calendar week."""

    week_number: int
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    classification: str = Field(..., pattern="^(teaching|holiday|examination)$")
    period_budget: Optional[int] = None
    label: Optional[str] = None


class TermInput(BaseModel):
    """Input schema for a calendar term."""

    order: int
    term_id_code: str
    title: str
    weeks: list[WeekInput] = []


class CalendarInput(BaseModel):
    """Input schema for creating/uploading calendar data."""

    academic_year: str
    terms: list[TermInput] = []


class TextbookEntryInput(BaseModel):
    """Input schema for a textbook reference entry."""

    sub_topic_id: int
    book_title: str
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    note: Optional[str] = None


# ==================== Response Schemas ====================


class ObjectiveResponse(BaseModel):
    """Response schema for a learning objective."""

    id: int
    order: int
    text: str

    model_config = {"from_attributes": True}


class SubTopicResponse(BaseModel):
    """Response schema for a sub-topic."""

    id: int
    order: int
    sub_topic_id_code: str
    title: str
    planned_periods: int
    competences: Optional[list[str]] = None
    objectives: list[ObjectiveResponse] = []

    model_config = {"from_attributes": True}


class TopicResponse(BaseModel):
    """Response schema for a topic."""

    id: int
    order: int
    topic_id_code: str
    title: str
    sub_topics: list[SubTopicResponse] = []

    model_config = {"from_attributes": True}


class SyllabusResponse(BaseModel):
    """Response schema for a syllabus."""

    id: int
    subject: str
    form: str
    source_note: Optional[str] = None
    created_at: datetime.datetime
    topics: list[TopicResponse] = []

    model_config = {"from_attributes": True}


class WeekResponse(BaseModel):
    """Response schema for a calendar week."""

    id: int
    week_number: int
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    classification: str
    period_budget: Optional[int] = None
    label: Optional[str] = None

    model_config = {"from_attributes": True}


class TermResponse(BaseModel):
    """Response schema for a calendar term."""

    id: int
    order: int
    term_id_code: str
    title: str
    weeks: list[WeekResponse] = []

    model_config = {"from_attributes": True}


class CalendarResponse(BaseModel):
    """Response schema for calendar data."""

    id: int
    academic_year: str
    created_at: datetime.datetime
    terms: list[TermResponse] = []

    model_config = {"from_attributes": True}


class AllocationAssignmentResponse(BaseModel):
    """Response schema for an allocation assignment."""

    id: int
    syllabus_id: int
    calendar_id: int
    week_id: int
    sub_topic_id: int
    slot: Optional[int] = None
    first_period: Optional[int] = None
    last_period: Optional[int] = None
    periods: int
    split_index: Optional[int] = None
    split_total: Optional[int] = None

    model_config = {"from_attributes": True}


class AllocationResponse(BaseModel):
    """Response schema for a full allocation result."""

    syllabus_id: int
    calendar_id: int
    assignments: list[AllocationAssignmentResponse] = []


class SchemeOfWorkEntry(BaseModel):
    """A single entry in the scheme of work output."""

    week_number: int
    week_label: Optional[str] = None
    term: str
    topic_title: str
    sub_topic_title: str
    objectives: list[str] = []
    periods: int
    teaching_methods: Optional[str] = None
    teaching_resources: Optional[str] = None
    references: Optional[str] = None


class SchemeOfWorkResponse(BaseModel):
    """Response schema for a complete scheme of work."""

    syllabus_id: int
    calendar_id: int
    subject: str
    form: str
    academic_year: str
    entries: list[SchemeOfWorkEntry] = []


class LessonPlanResponse(BaseModel):
    """Response schema for a lesson plan."""

    id: int
    assignment_id: int
    period_number: int
    date: Optional[datetime.date] = None
    teacher_activities: Optional[str] = None
    student_activities: Optional[str] = None
    assessment: Optional[str] = None
    consolidation: Optional[str] = None
    teaching_resources: Optional[str] = None
    remarks: Optional[str] = None

    model_config = {"from_attributes": True}


class TextbookEntryResponse(BaseModel):
    """Response schema for a textbook entry."""

    id: int
    sub_topic_id: int
    book_title: str
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    note: Optional[str] = None

    model_config = {"from_attributes": True}
