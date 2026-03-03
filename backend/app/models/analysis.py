from datetime import datetime
from mongoengine import (
    Document,
    DictField,
    FloatField,
    IntField,
    DateTimeField,
    StringField,
    ReferenceField,
)

from app.models.user import User


# ── Event-Driven Behavioral Storage ──────────────────────────────────────────
class BehaviorEvent(Document):
    """Raw behavioral event stream. Never aggregated away — always queryable."""
    user       = ReferenceField(User, required=True)
    event_type = StringField(required=True)   # commit | pull_request | issue | review_comment
    timestamp  = DateTimeField(required=True)
    metadata   = DictField(default=dict)

    meta = {
        "collection": "events",
        "indexes": ["user", "event_type", "-timestamp"],
    }


# ── Derived Feature Layer ─────────────────────────────────────────────────────
class FeatureMetrics(Document):
    user                  = ReferenceField(User, required=True)
    commit_consistency    = FloatField(required=True)
    focus_depth           = FloatField(required=True)
    collaboration_index   = FloatField(required=True)
    experimentation_index = FloatField(required=True)
    persistence_index     = FloatField(required=True)
    complexity_handling   = FloatField(required=True)
    # Extended context signals
    total_commits         = IntField(default=0)
    total_repos           = IntField(default=0)
    night_commit_ratio    = FloatField(default=0.0)
    avg_commit_hour       = FloatField(default=12.0)
    burst_session_count   = IntField(default=0)
    # Enriched signals
    language_diversity    = FloatField(default=0.0)
    pr_merge_ratio        = FloatField(default=0.0)
    avg_files_per_commit  = FloatField(default=0.0)
    code_churn_ratio      = FloatField(default=0.0)
    active_days_ratio     = FloatField(default=0.0)
    computed_at           = DateTimeField(default=datetime.utcnow)


# ── Personality + Intelligence Layer ─────────────────────────────────────────
class PersonalitySnapshot(Document):
    user               = ReferenceField(User, required=True)
    week               = StringField()           # ISO week e.g. "2026-W09"
    # Core traits (0-100)
    analytical         = FloatField(required=True)
    creativity         = FloatField(required=True)
    discipline         = FloatField(required=True)
    collaboration      = FloatField(required=True)
    adaptability       = FloatField(required=True)
    learning_velocity  = FloatField(required=True)
    risk_appetite      = FloatField(required=True)
    stress_stability   = FloatField(required=True)
    # Interpretability layer
    reasoning          = DictField(default=dict)   # trait → human-readable reason
    # Role prediction
    predicted_role     = StringField(default="")
    role_reason        = StringField(default="")
    role_confidence    = FloatField(default=0.0)
    # Work style
    work_style         = StringField(default="")
    work_style_detail  = StringField(default="")
    created_at         = DateTimeField(default=datetime.utcnow)


# ── Job Tracking ──────────────────────────────────────────────────────────────
class AnalysisJob(Document):
    user        = ReferenceField(User, required=True)
    status      = StringField(required=True, default="queued")
    progress    = IntField(default=0)
    message     = StringField(default="")
    logs        = StringField(default="")
    created_at  = DateTimeField(default=datetime.utcnow)
    finished_at = DateTimeField()

