import threading
from datetime import datetime
from bson import ObjectId

from app.core.celery_app import celery_app
from app.core.database import init_db, close_db
from app.feature_engineering.metrics import compute_metrics
from app.github_ingestion.ingest import GitHubIngestor
from app.models.analysis import AnalysisJob, FeatureMetrics, PersonalitySnapshot
from app.models.github import GitHubAccount
from app.models.user import User
from app.personality_engine.engine import infer_personality

# Limits — deeper analysis with more data points for accuracy
MAX_REPOS   = 20
MAX_COMMITS = 50


def _append_log(job: AnalysisJob, line: str) -> None:
    ts = datetime.utcnow().strftime("%H:%M:%S")
    job.logs = (job.logs or "") + f"[{ts}] {line}\n"
    job.save()


def _run_analysis_sync(user_id: str) -> None:
    init_db()
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return

    job = AnalysisJob(
        user=user, status="running", progress=5,
        message="Starting analysis", logs=""
    ).save()

    try:
        account = GitHubAccount.objects(user=user).first()
        if not account:
            raise RuntimeError("GitHub account not connected")

        _append_log(job, f"Connected as {account.github_login}")
        job.progress = 10; job.message = "Fetching GitHub repositories"; job.save()

        ingestor = GitHubIngestor(account, max_repos=MAX_REPOS, max_commits=MAX_COMMITS)
        total_repos, total_commits = ingestor.ingest(log_fn=lambda msg: _append_log(job, msg))

        _append_log(job, f"Ingested {total_repos} repos, {total_commits} commits")
        job.progress = 60; job.message = "Computing behavioral metrics"; job.save()

        metrics = compute_metrics(user_id)
        _append_log(job, f"Metrics: {total_commits} commits | {metrics['pull_requests']} PRs | "
                         f"night_ratio={metrics['night_commit_ratio']:.0%}")

        FeatureMetrics(
            user=user,
            commit_consistency=metrics["commit_consistency"],
            focus_depth=metrics["focus_depth"],
            collaboration_index=metrics["collaboration_index"],
            experimentation_index=metrics["experimentation_index"],
            persistence_index=metrics["persistence_index"],
            complexity_handling=metrics["complexity_handling"],
            total_commits=metrics["total_commits"],
            total_repos=metrics["total_repos"],
            night_commit_ratio=metrics["night_commit_ratio"],
            avg_commit_hour=metrics["avg_commit_hour"],
            burst_session_count=metrics["burst_session_count"],
            language_diversity=metrics["language_diversity"],
            pr_merge_ratio=metrics["pr_merge_ratio"],
            avg_files_per_commit=metrics["avg_files_per_commit"],
            code_churn_ratio=metrics["code_churn_ratio"],
            active_days_ratio=metrics["active_days_ratio"],
        ).save()

        job.progress = 80; job.message = "Inferring personality + role fit"; job.save()
        _append_log(job, "Running behavioral inference engine")

        insight = infer_personality(metrics)

        # ISO week label e.g. "2026-W09"
        week = datetime.utcnow().strftime("%Y-W%V")

        PersonalitySnapshot(
            user=user,
            week=week,
            analytical=insight["analytical"],
            creativity=insight["creativity"],
            discipline=insight["discipline"],
            collaboration=insight["collaboration"],
            adaptability=insight["adaptability"],
            learning_velocity=insight["learning_velocity"],
            risk_appetite=insight["risk_appetite"],
            stress_stability=insight["stress_stability"],
            reasoning=insight["reasoning"],
            predicted_role=insight["predicted_role"],
            role_reason=insight["role_reason"],
            role_confidence=insight["role_confidence"],
            work_style=insight["work_style"],
            work_style_detail=insight["work_style_detail"],
        ).save()

        _append_log(job, f"Role predicted: {insight['predicted_role']} ({insight['role_confidence']}%)")
        _append_log(job, f"Work style: {insight['work_style']}")
        _append_log(job, "Analysis complete ✓")

        job.progress = 100; job.status = "completed"
        job.message = "Analysis complete"
        job.finished_at = datetime.utcnow()
        job.save()

    except Exception as exc:
        _append_log(job, f"ERROR: {exc}")
        job.status = "failed"
        job.message = str(exc)
        job.finished_at = datetime.utcnow()
        job.save()
    finally:
        close_db()


@celery_app.task
def run_analysis(user_id: str):
    _run_analysis_sync(user_id)


def run_analysis_background(user_id: str) -> None:
    t = threading.Thread(target=_run_analysis_sync, args=(user_id,), daemon=True)
    t.start()

