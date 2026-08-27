# Scheme of Work & Lesson Plan Generator

A FastAPI application that automatically generates **Schemes of Work** and **Lesson Plans** as `.docx` documents from structured syllabus and academic calendar data.

Built for the Tanzania O-Level secondary education system, currently seeded with the **Form I Basic Mathematics** syllabus (2023 TIE curriculum).

## Features

- **Syllabus Management** - Store and retrieve structured syllabus data (topics, sub-topics, competences, objectives)
- **Academic Calendar** - Define terms, teaching weeks, holidays, and examination periods with period budgets
- **Textbook References** - Link textbook entries to sub-topics for automatic citation in outputs
- **Allocation Engine** - Automatically distribute sub-topics across teaching weeks based on period budgets
- **Scheme of Work Generation** - Produce a complete scheme of work table with all 12 columns (week, dates, topic, sub-topic, periods, objectives, teaching/learning strategies, resources, assessment, references, remarks, teacher's self-evaluation)
- **Lesson Plan Generation** - Generate per-period lesson plans with stages (Introduction, Development, Consolidation, Conclusion), timing, teacher/student activities, and assessment
- **DOCX Export** - Download publication-ready `.docx` files for both scheme of work and lesson plans

## Prerequisites

- Python 3.11 or higher (3.12 recommended)
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/kiyaboapp/scheme-of-work-and-lesson-plans.git
cd scheme-of-work-and-lesson-plans

# Create virtual environment and install dependencies (using uv)
uv venv venv
uv pip install -e '.[dev]'

# Or using pip
python -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
```

## Quick Start

### 1. Seed the Database

Populate the database with Form I Mathematics syllabus, 2026 academic calendar, textbook references, and run the allocation engine:

```bash
venv/bin/python seed/seed_form1_math.py
```

This creates `sow_generator.db` (SQLite) with:
- 3 topics, 5 sub-topics totaling 175 periods
- 2 terms with 35 teaching weeks (5 periods/week)
- 5 textbook entries
- 36 allocation assignments covering all 175 periods

### 2. Generate Example DOCX Files

Run the full pipeline (fresh database, seed, then generate documents):

```bash
venv/bin/python seed/generate_examples.py
```

This produces two files in the `examples/` directory:
- `Scheme_of_Work_Form1_Mathematics_2026.docx` - Complete scheme of work table
- `Lesson_Plans_Form1_Mathematics_2026.docx` - All lesson plans for the year

### 3. Start the API Server

```bash
venv/bin/python -m uvicorn app.main:app --reload
```

The server runs at `http://localhost:8000`. Interactive API docs are available at `http://localhost:8000/docs`.

## API Endpoints

### Syllabus

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/syllabus/` | Create a new syllabus with topics and sub-topics |
| GET | `/api/syllabus/` | List all syllabuses |
| GET | `/api/syllabus/{id}` | Get a syllabus by ID with full nested structure |

### Calendar

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/calendar/` | Create an academic calendar with terms and weeks |
| GET | `/api/calendar/` | List all calendars |
| GET | `/api/calendar/{id}` | Get a calendar by ID with terms and weeks |

### Textbook

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/textbook/` | Create textbook reference entries (bulk) |
| GET | `/api/textbook/` | List all textbook entries |

### Allocation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/allocate` | Run the allocation engine for a syllabus/calendar pair |
| GET | `/api/allocate/{syllabus_id}/{calendar_id}` | Retrieve existing allocation results |

### Scheme of Work

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scheme/{syllabus_id}/{calendar_id}` | Generate scheme of work (JSON) |
| GET | `/api/scheme/{syllabus_id}/{calendar_id}/docx` | Download scheme of work as .docx |

### Lesson Plans

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lesson-plan/{syllabus_id}/{calendar_id}/week/{week_number}` | Get lesson plans for a week (JSON) |
| GET | `/api/lesson-plan/{syllabus_id}/{calendar_id}/week/{week_number}/period/{period_number}` | Get a single lesson plan (JSON) |
| GET | `/api/lesson-plan/{syllabus_id}/{calendar_id}/docx` | Download all lesson plans as .docx |

## Examples Directory

The `examples/` directory contains pre-generated `.docx` files that demonstrate what the system produces:

- **Scheme_of_Work_Form1_Mathematics_2026.docx** - A complete scheme of work for Form I Basic Mathematics covering the 2026 academic year. Contains a 12-column table with topics allocated across 35 teaching weeks.
- **Lesson_Plans_Form1_Mathematics_2026.docx** - Individual lesson plans for every teaching period (175 total). Each plan includes learning objectives, teaching stages with timing, teacher and student activities, and assessment criteria.

These files are generated from the Form I Mathematics seed data and serve as reference examples of the output format.

## Running Tests

```bash
# Run all tests with verbose output
venv/bin/python -m pytest tests/ -v

# Run a specific test file
venv/bin/python -m pytest tests/test_docx_generation.py -v
```

## Project Structure

```
app/
  main.py              - FastAPI application entry point
  database.py          - SQLAlchemy engine and session setup
  models.py            - ORM models (Syllabus, Topic, SubTopic, Calendar, Term, Week, etc.)
  schemas.py           - Pydantic request/response schemas
  routers/             - API route handlers
  services/            - Business logic (allocation, scheme generation, docx writers)
seed/
  seed_form1_math.py   - Seed script with Form I Mathematics data
  generate_examples.py - Runner that seeds + generates example .docx files
examples/              - Pre-generated .docx output files
tests/                 - pytest test suite
assets/                - Source PDFs and sample documents
tools/                 - Text extractions from source documents
```

## Technology Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM and database management
- **Pydantic** - Data validation and serialization
- **python-docx** - DOCX file generation
- **SQLite** - Database (file-based, no server required)
- **pytest + httpx** - Testing
