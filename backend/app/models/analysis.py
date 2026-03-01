from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FeatureMetrics(Base):
    __tablename__ = "feature_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commit_consistency = Column(Float, nullable=False)
    focus_depth = Column(Float, nullable=False)
    collaboration_index = Column(Float, nullable=False)
    experimentation_index = Column(Float, nullable=False)
    persistence_index = Column(Float, nullable=False)
    complexity_handling = Column(Float, nullable=False)
    computed_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="feature_metrics")


class PersonalitySnapshot(Base):
    __tablename__ = "personality_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analytical = Column(Float, nullable=False)
    creativity = Column(Float, nullable=False)
    discipline = Column(Float, nullable=False)
    collaboration = Column(Float, nullable=False)
    adaptability = Column(Float, nullable=False)
    learning_velocity = Column(Float, nullable=False)
    risk_appetite = Column(Float, nullable=False)
    stress_stability = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="personality_snapshots")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="queued")
    progress = Column(Integer, default=0)
    message = Column(String, default="")
    created_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime)

    user = relationship("User", back_populates="analysis_jobs")
