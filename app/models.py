"""SQLAlchemy ORM models for the SOW Generator application."""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class WeekClassification(str, enum.Enum):
    """Classification of a calendar week."""

    teaching = "teaching"
    holiday = "holiday"
    examination = "examination"


class Syllabus(Base):
    """Top-level syllabus entity representing a subject syllabus."""

    __tablename__ = "syllabuses"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    form = Column(String, nullable=False)
    source_note = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    topics = relationship("Topic", back_populates="syllabus", cascade="all, delete-orphan")


class Topic(Base):
    """A topic within a syllabus."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    syllabus_id = Column(Integer, ForeignKey("syllabuses.id"), nullable=False)
    order = Column(Integer, nullable=False)
    topic_id_code = Column(String, nullable=False)
    title = Column(String, nullable=False)

    syllabus = relationship("Syllabus", back_populates="topics")
    sub_topics = relationship("SubTopic", back_populates="topic", cascade="all, delete-orphan")


class SubTopic(Base):
    """A sub-topic within a topic, with planned periods."""

    __tablename__ = "sub_topics"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    order = Column(Integer, nullable=False)
    sub_topic_id_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    planned_periods = Column(Integer, nullable=False)
    competences = Column(JSON, nullable=True)

    topic = relationship("Topic", back_populates="sub_topics")
    objectives = relationship("Objective", back_populates="sub_topic", cascade="all, delete-orphan")
    textbook_entries = relationship("TextbookEntry", back_populates="sub_topic", cascade="all, delete-orphan")
    allocation_assignments = relationship("AllocationAssignment", back_populates="sub_topic")


class Objective(Base):
    """A learning objective within a sub-topic."""

    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, index=True)
    sub_topic_id = Column(Integer, ForeignKey("sub_topics.id"), nullable=False)
    order = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    sub_topic = relationship("SubTopic", back_populates="objectives")


class CalendarData(Base):
    """Academic calendar data for a given year."""

    __tablename__ = "calendar_data"

    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    terms = relationship("Term", back_populates="calendar", cascade="all, delete-orphan")


class Term(Base):
    """A term within an academic calendar."""

    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    calendar_id = Column(Integer, ForeignKey("calendar_data.id"), nullable=False)
    order = Column(Integer, nullable=False)
    term_id_code = Column(String, nullable=False)
    title = Column(String, nullable=False)

    calendar = relationship("CalendarData", back_populates="terms")
    weeks = relationship("Week", back_populates="term", cascade="all, delete-orphan")


class Week(Base):
    """A week within a term, classified by type."""

    __tablename__ = "weeks"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    classification = Column(Enum(WeekClassification), nullable=False)
    period_budget = Column(Integer, nullable=True)
    label = Column(String, nullable=True)

    term = relationship("Term", back_populates="weeks")
    allocation_assignments = relationship("AllocationAssignment", back_populates="week")


class TextbookEntry(Base):
    """Reference mapping a sub-topic to pages in a textbook."""

    __tablename__ = "textbook_entries"

    id = Column(Integer, primary_key=True, index=True)
    sub_topic_id = Column(Integer, ForeignKey("sub_topics.id"), nullable=False)
    book_title = Column(String, nullable=False)
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)
    note = Column(String, nullable=True)

    sub_topic = relationship("SubTopic", back_populates="textbook_entries")


class AllocationAssignment(Base):
    """Assignment of a sub-topic (or portion) to a specific week via bin-packing."""

    __tablename__ = "allocation_assignments"

    id = Column(Integer, primary_key=True, index=True)
    syllabus_id = Column(Integer, ForeignKey("syllabuses.id"), nullable=False)
    calendar_id = Column(Integer, ForeignKey("calendar_data.id"), nullable=False)
    week_id = Column(Integer, ForeignKey("weeks.id"), nullable=False)
    sub_topic_id = Column(Integer, ForeignKey("sub_topics.id"), nullable=False)
    slot = Column(Integer, nullable=True)
    first_period = Column(Integer, nullable=True)
    last_period = Column(Integer, nullable=True)
    periods = Column(Integer, nullable=False)
    split_index = Column(Integer, nullable=True)
    split_total = Column(Integer, nullable=True)

    syllabus = relationship("Syllabus")
    calendar = relationship("CalendarData")
    week = relationship("Week", back_populates="allocation_assignments")
    sub_topic = relationship("SubTopic", back_populates="allocation_assignments")
    lesson_plans = relationship("LessonPlan", back_populates="assignment", cascade="all, delete-orphan")


class LessonPlan(Base):
    """A lesson plan for a specific period within an allocation assignment."""

    __tablename__ = "lesson_plans"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("allocation_assignments.id"), nullable=False)
    period_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=True)
    teacher_activities = Column(Text, nullable=True)
    student_activities = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    consolidation = Column(Text, nullable=True)
    teaching_resources = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)

    assignment = relationship("AllocationAssignment", back_populates="lesson_plans")
