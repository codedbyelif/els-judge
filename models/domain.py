from sqlalchemy import Column, Integer, String, Text, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    original_code = Column(Text, nullable=False)
    suggested_code = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    reviews = relationship("Review", back_populates="submission", cascade="all, delete-orphan")
    diffs = relationship("DiffNode", back_populates="submission", cascade="all, delete-orphan")
    verdict = relationship("FinalVerdict", back_populates="submission", uselist=False, cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    model_name = Column(String(50), nullable=False)
    raw_response = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=False) # The JSON extracted from LLM
    risk_score = Column(Float, default=0.0)
    
    submission = relationship("Submission", back_populates="reviews")

class DiffNode(Base):
    __tablename__ = "diff_nodes"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    change_type = Column(String(20), nullable=False) # e.g. 'insert', 'delete', 'replace'
    original_chunk = Column(Text, nullable=True)
    suggested_chunk = Column(Text, nullable=True)
    
    submission = relationship("Submission", back_populates="diffs")

class FinalVerdict(Base):
    __tablename__ = "final_verdicts"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    aggregated_risk_score = Column(Float, nullable=False)
    severity_level = Column(String(20), nullable=False) # e.g., Low, Medium, High, Critical
    disagreement_rate = Column(Float, nullable=False)
    consensus_issues = Column(JSON, nullable=False) # Summarized issues
    markdown_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    submission = relationship("Submission", back_populates="verdict")
