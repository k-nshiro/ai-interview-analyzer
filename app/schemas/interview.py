from pydantic import BaseModel, Field
from typing import Optional 

# Contract for starting a new interview
class InterviewStart(BaseModel):
    role: str = Field(..., example="Backed Engineer", description="The job role being interviews for")
    experience_level: str = Field(...,example="Intermediate", description="Fresher, Intermediate, or Senior")
    tech_stack: list[str] = Field(default=[], example=["Python", "FastAPI", "PostSQL"])


# Contract for what we send back to the user (the QUESTION)
class QuestionResponse(BaseModel):
    question_id: int
    text: str
    difficulty: str = Field(..., example="Medium")
    session_id: Optional[int] = Field(default=None, description="The interview session ID this question belongs to")


# Contract for the user submitting their voice/text answer
class AnswerSubmit(BaseModel): 
    question_id: int = Field(..., description="The ID of the question being answered")
    answer_text: str = Field(..., min_length=10, description= "The transcribed text of the user's answer")
    time_taken_seconds: Optional[int] = None