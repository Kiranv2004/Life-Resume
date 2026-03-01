from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.analysis import AnalysisJob, FeatureMetrics, PersonalitySnapshot
from app.schemas.analysis import AnalysisJobOut, FeatureMetricsOut, PersonalitySnapshotOut

router = APIRouter()


@router.get("/job", response_model=AnalysisJobOut)
def latest_job(db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.user_id == user.id)
        .order_by(AnalysisJob.created_at.desc())
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="No analysis job found")
    return job


@router.get("/metrics", response_model=FeatureMetricsOut)
def latest_metrics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    metrics = (
        db.query(FeatureMetrics)
        .filter(FeatureMetrics.user_id == user.id)
        .order_by(FeatureMetrics.computed_at.desc())
        .first()
    )
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found")
    return metrics


@router.get("/personality", response_model=PersonalitySnapshotOut)
def latest_personality(db: Session = Depends(get_db), user=Depends(get_current_user)):
    snapshot = (
        db.query(PersonalitySnapshot)
        .filter(PersonalitySnapshot.user_id == user.id)
        .order_by(PersonalitySnapshot.created_at.desc())
        .first()
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="No personality snapshot found")
    return snapshot


@router.get("/history", response_model=list[PersonalitySnapshotOut])
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    snapshots = (
        db.query(PersonalitySnapshot)
        .filter(PersonalitySnapshot.user_id == user.id)
        .order_by(PersonalitySnapshot.created_at.asc())
        .all()
    )
    return snapshots
