from datetime import datetime
from pydantic import BaseModel


class FeatureMetricsOut(BaseModel):
    commit_consistency: float
    focus_depth: float
    collaboration_index: float
    experimentation_index: float
    persistence_index: float
    complexity_handling: float
    computed_at: datetime

    class Config:
        from_attributes = True


class PersonalitySnapshotOut(BaseModel):
    analytical: float
    creativity: float
    discipline: float
    collaboration: float
    adaptability: float
    learning_velocity: float
    risk_appetite: float
    stress_stability: float
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisJobOut(BaseModel):
    id: int
    status: str
    progress: int
    message: str

    class Config:
        from_attributes = True
