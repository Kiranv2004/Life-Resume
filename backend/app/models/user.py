from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    github_account = relationship("GitHubAccount", uselist=False, back_populates="user")
    feature_metrics = relationship("FeatureMetrics", back_populates="user")
    personality_snapshots = relationship("PersonalitySnapshot", back_populates="user")
    analysis_jobs = relationship("AnalysisJob", back_populates="user")
