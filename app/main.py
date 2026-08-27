"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import allocation, calendar, lesson_plan, scheme, syllabus, textbook


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SOW Generator",
    description="Generate Schemes of Work and Lesson Plans from syllabus and calendar data",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(syllabus.router)
app.include_router(calendar.router)
app.include_router(textbook.router)
app.include_router(allocation.router)
app.include_router(scheme.router)
app.include_router(lesson_plan.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
