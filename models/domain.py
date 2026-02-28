from sqlalchemy import Column, Integer, String, Text, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suggestions = relationship("ModelSuggestion", back_populates="submission", cascade="all, delete-orphan")

class ModelSuggestion(Base):
    __tablename__ = "model_suggestions"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    model_name = Column(String(100), nullable=False)
    improved_code = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)
    diff_text = Column(Text, nullable=True)
    markdown_report = Column(Text, nullable=True)

    submission = relationship("Submission", back_populates="suggestions")
