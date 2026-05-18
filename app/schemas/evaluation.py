from typing import Optional
from pydantic import BaseModel, Field

# Contract for the AI's grading of a single answer
class AnswerEvaluation(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score from 0 to 10")
    feedback: str = Field(..., description="Direct feedback to the candidate")
    strengths: list[str] = Field(default=[], description="Key positive points in the answer")
    weaknesses: list[str] = Field(default=[], description="Missing keywords or concepts")
    ideal_answer_snippet: str = Field(default="", description="A short example of what a perfect answer looks like")
    confidence_detected: str = Field(..., example="High", description="High, Medium, or Low based on tone/words")

# Contract for generating the NEXT question
class NextQuestionGen(BaseModel):
    question_id: Optional[int] = Field(default=None, description="The database ID for this new question")
    next_question: str = Field(..., description="The next question text")
    difficulty: str = Field(..., description="Easy, Medium, or Hard")

# This is the response we will send back to the frontend
class EvaluationResult(BaseModel):
    evaluation: AnswerEvaluation
    next_question: NextQuestionGen