from datetime import datetime
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.feature_engineering.metrics import compute_metrics
from app.github_ingestion.ingest import GitHubIngestor
from app.models.analysis import AnalysisJob, FeatureMetrics, PersonalitySnapshot
from app.models.github import GitHubAccount
from app.personality_engine.engine import infer_personality


@celery_app.task
def run_analysis(user_id: int):
    db: Session = SessionLocal()
    job = AnalysisJob(user_id=user_id, status="running", progress=0, message="Starting")
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        account = db.query(GitHubAccount).filter(GitHubAccount.user_id == user_id).first()
        if not account:
            raise RuntimeError("GitHub account not connected")
        job.progress = 10
        job.message = "Fetching GitHub data"
        db.commit()

        GitHubIngestor(db, account).ingest()

        job.progress = 50
        job.message = "Computing feature metrics"
        db.commit()

        metrics = compute_metrics(db, user_id)
        feature = FeatureMetrics(
            user_id=user_id,
            commit_consistency=metrics["commit_consistency"],
            focus_depth=metrics["focus_depth"],
            collaboration_index=metrics["collaboration_index"],
            experimentation_index=metrics["experimentation_index"],
            persistence_index=metrics["persistence_index"],
            complexity_handling=metrics["complexity_handling"],
        )
        db.add(feature)
        db.commit()

        job.progress = 75
        job.message = "Inferring personality"
        db.commit()

        personality = infer_personality(metrics)
        snapshot = PersonalitySnapshot(user_id=user_id, **personality)
        db.add(snapshot)
        db.commit()

        job.progress = 100
        job.status = "completed"
        job.message = "Completed"
        job.finished_at = datetime.utcnow()
        db.commit()
    except Exception as exc:
        job.status = "failed"
        job.message = str(exc)
        job.finished_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()
