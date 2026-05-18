from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)
    experience_level = Column(String)

    # Link a session to all of its questions and answers
    qa_history = relationship("QuestionAnswer", back_populates="session", cascade="all, delete-orphan")

class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))

    question_text = Column(Text)
    difficulty = Column(String)

    # These start as null until user answers
    user_answer = Column(Text, nullable=True)
    ai_score = Column(Float, nullable=True)
    ai_feedback = Column(Text, nullable=True)

    session = relationship("InterviewSession", back_populates="qa_history")