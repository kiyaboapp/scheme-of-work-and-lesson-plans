"""
Generate example .docx files (Scheme of Work and Lesson Plans).

This script:
1. Removes any existing sow_generator.db (to start fresh)
2. Runs the seed to populate the database with Form I Mathematics data
3. Uses TestClient to call the .docx endpoints
4. Saves the generated files to the examples/ directory
5. Prints a summary with file sizes

Usage:
    cd /projects/sandbox/scheme-of-work-and-lesson-plans
    .venv/bin/python seed/generate_examples.py
"""

import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Remove existing database to start fresh
DB_PATH = PROJECT_ROOT / "sow_generator.db"
if DB_PATH.exists():
    os.remove(DB_PATH)
    print(f"Removed existing database: {DB_PATH.name}")

from fastapi.testclient import TestClient

from app.main import app
from seed.seed_form1_math import run_seed

EXAMPLES_DIR = PROJECT_ROOT / "examples"


def generate_examples():
    """Run the full pipeline: seed data then generate .docx example files."""
    # Step 1: Run the seed to populate the database
    print("\n" + "=" * 60)
    print("  GENERATING EXAMPLE .DOCX FILES")
    print("=" * 60)

    result = run_seed()
    syllabus_id = result["syllabus_id"]
    calendar_id = result["calendar_id"]

    # Step 2: Create the examples directory
    EXAMPLES_DIR.mkdir(exist_ok=True)

    client = TestClient(app)

    # Step 3: Generate Scheme of Work .docx
    print("\n[docx] Generating Scheme of Work .docx...")
    resp = client.get(f"/api/scheme/{syllabus_id}/{calendar_id}/docx")
    if resp.status_code != 200:
        print(f"  ERROR generating scheme docx: {resp.status_code} - {resp.text}")
        sys.exit(1)

    scheme_path = EXAMPLES_DIR / "Scheme_of_Work_Form1_Mathematics_2026.docx"
    scheme_path.write_bytes(resp.content)
    print(f"  Saved: {scheme_path.relative_to(PROJECT_ROOT)}")

    # Step 4: Generate Lesson Plans .docx
    print("[docx] Generating Lesson Plans .docx...")
    resp = client.get(f"/api/lesson-plan/{syllabus_id}/{calendar_id}/docx")
    if resp.status_code != 200:
        print(f"  ERROR generating lesson plan docx: {resp.status_code} - {resp.text}")
        sys.exit(1)

    lesson_path = EXAMPLES_DIR / "Lesson_Plans_Form1_Mathematics_2026.docx"
    lesson_path.write_bytes(resp.content)
    print(f"  Saved: {lesson_path.relative_to(PROJECT_ROOT)}")

    # Step 5: Print summary
    print("\n" + "=" * 60)
    print("  EXAMPLE FILES GENERATED")
    print("=" * 60)
    print(f"  Directory: {EXAMPLES_DIR.relative_to(PROJECT_ROOT)}/")
    print()
    for f in sorted(EXAMPLES_DIR.glob("*.docx")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:50s} {size_kb:>8.1f} KB")
    print()
    print("=" * 60)


if __name__ == "__main__":
    generate_examples()
