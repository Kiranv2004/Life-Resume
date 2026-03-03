from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class FeatureMetricsOut(BaseModel):
    commit_consistency:    float
    focus_depth:           float
    collaboration_index:   float
    experimentation_index: float
    persistence_index:     float
    complexity_handling:   float
    total_commits:         int = 0
    total_repos:           int = 0
    night_commit_ratio:    float = 0.0
    avg_commit_hour:       float = 12.0
    burst_session_count:   int = 0
    language_diversity:    float = 0.0
    pr_merge_ratio:        float = 0.0
    avg_files_per_commit:  float = 0.0
    code_churn_ratio:      float = 0.0
    active_days_ratio:     float = 0.0
    computed_at:           datetime

    class Config:
        from_attributes = True


class PersonalitySnapshotOut(BaseModel):
    analytical:        float
    creativity:        float
    discipline:        float
    collaboration:     float
    adaptability:      float
    learning_velocity: float
    risk_appetite:     float
    stress_stability:  float
    week:              Optional[str] = None
    reasoning:         Dict[str, str] = {}
    predicted_role:    str = ""
    role_reason:       str = ""
    role_confidence:   float = 0.0
    work_style:        str = ""
    work_style_detail: str = ""
    created_at:        datetime

    class Config:
        from_attributes = True


class AnalysisJobOut(BaseModel):
    id:       str
    status:   str
    progress: int
    message:  str
    logs:     str = ""

    class Config:
        from_attributes = True
