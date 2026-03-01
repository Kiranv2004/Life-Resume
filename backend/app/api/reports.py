from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.analysis import FeatureMetrics, PersonalitySnapshot
from app.report_generator.report import generate_report
from app.services.report_store import save_report

router = APIRouter()


@router.get("/download")
def download_report(db: Session = Depends(get_db), user=Depends(get_current_user)):
    metrics = (
        db.query(FeatureMetrics)
        .filter(FeatureMetrics.user_id == user.id)
        .order_by(FeatureMetrics.computed_at.desc())
        .first()
    )
    snapshot = (
        db.query(PersonalitySnapshot)
        .filter(PersonalitySnapshot.user_id == user.id)
        .order_by(PersonalitySnapshot.created_at.desc())
        .first()
    )
    if not metrics or not snapshot:
        raise HTTPException(status_code=404, detail="No analysis data available")
    metrics_data = {
        "commit_consistency": metrics.commit_consistency,
        "focus_depth": metrics.focus_depth,
        "collaboration_index": metrics.collaboration_index,
        "experimentation_index": metrics.experimentation_index,
        "persistence_index": metrics.persistence_index,
        "complexity_handling": metrics.complexity_handling,
    }
    personality_data = {
        "analytical": snapshot.analytical,
        "creativity": snapshot.creativity,
        "discipline": snapshot.discipline,
        "collaboration": snapshot.collaboration,
        "adaptability": snapshot.adaptability,
        "learning_velocity": snapshot.learning_velocity,
        "risk_appetite": snapshot.risk_appetite,
        "stress_stability": snapshot.stress_stability,
    }
    report_bytes = generate_report(user.email, metrics_data, personality_data)
    path = save_report(user.id, report_bytes)
    return FileResponse(path, filename=path.split("/")[-1])
