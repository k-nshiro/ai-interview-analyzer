from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models.interview import InterviewSession
from app.schemas.report import InterviewReport
from app.ai.llm_client import generate_final_report

router = APIRouter()

@router.get("/{session_id}", response_model=InterviewReport)
async def get_interview_report(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the entire interview history for a session and generates a final AI report.
    """
    # 1. Fetch the session and ALL its questions/answers from the DB at the same time
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.qa_history))
        .where(InterviewSession.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    if not session.qa_history:
        raise HTTPException(status_code=400, detail="No questions have been answered yet in this session.")

    # 2. Build the Transcript string for the AI
    transcript = ""
    for i, qa in enumerate(session.qa_history, 1):
        # We only want to include questions that the user actually answered
        if qa.user_answer:
            transcript += f"Q{i}: {qa.question_text}\n"
            transcript += f"Candidate Answer: {qa.user_answer}\n"
            transcript += "-" * 20 + "\n"

    # 3. Call the AI Reporter
    try:
        report = await generate_final_report(
            role=session.role,
            experience_level=session.experience_level,
            transcript=transcript
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate the AI report.")