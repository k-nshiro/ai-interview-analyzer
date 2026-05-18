from app.schemas.evaluation import AnswerEvaluation, EvaluationResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.interview import InterviewStart, QuestionResponse, AnswerSubmit

from app.services import interview_mgr
from app.db.session import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Interview system is online."}

@router.post("/start", response_model=QuestionResponse)
async def start_interview(
    request: InterviewStart, 
    db: AsyncSession = Depends(get_db) # Automatically opens & closes DB connection safely
):
    """
    Starts a new interview session and returns the first question.
    """
    return await interview_mgr.start_new_interview(request, db)

@router.post("/evaluate", response_model=EvaluationResult)
async def submit_answer(
    answer: AnswerSubmit,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits an answer, gets evaluated, and returns the AI's feedback + the NEXT question.
    """
    try:
        return await interview_mgr.process_answer(answer_data=answer, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 

@router.get("/report/{session_id}")
async def get_interview_report(session_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetches the final dynamically calculated report for a completed session.
    """
    try:
        # Calls the new dynamic math function we just added to interview_mgr.py!
        report = await interview_mgr.generate_final_report(session_id, db)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))