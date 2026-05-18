from pydantic import BaseModel, Field

class InterviewReport(BaseModel):
    final_score: float = Field(..., ge=0, le=10, description="Overall score out of 10")
    summary: str = Field(..., description="Executive summary of the candidate's performance")
    top_strengths: list[str] = Field(..., description="Top 3 technical strengths")
    top_weaknesses: list[str] = Field(..., description="Top 3 knowledge gaps")
    recommended_study_topics: list[str] = Field(..., description="Actionable study topics")