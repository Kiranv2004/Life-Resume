from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from app.auth.dependencies import get_current_user
from app.models.analysis import AnalysisJob, BehaviorEvent, FeatureMetrics, PersonalitySnapshot
from app.models.github import GitHubAccount, GitHubRepo, Commit
from app.schemas.analysis import AnalysisJobOut, FeatureMetricsOut, PersonalitySnapshotOut

router = APIRouter()


@router.get("/job", response_model=AnalysisJobOut)
def latest_job(user=Depends(get_current_user)):
    job = AnalysisJob.objects(user=user).order_by("-created_at").first()
    if not job:
        raise HTTPException(status_code=404, detail="No analysis job found")
    return AnalysisJobOut(
        id=str(job.id), status=job.status, progress=job.progress,
        message=job.message, logs=job.logs or "",
    )


@router.get("/metrics", response_model=FeatureMetricsOut)
def latest_metrics(user=Depends(get_current_user)):
    m = FeatureMetrics.objects(user=user).order_by("-computed_at").first()
    if not m:
        raise HTTPException(status_code=404, detail="No metrics found")
    return FeatureMetricsOut(
        commit_consistency=m.commit_consistency,
        focus_depth=m.focus_depth,
        collaboration_index=m.collaboration_index,
        experimentation_index=m.experimentation_index,
        persistence_index=m.persistence_index,
        complexity_handling=m.complexity_handling,
        total_commits=m.total_commits or 0,
        total_repos=m.total_repos or 0,
        night_commit_ratio=m.night_commit_ratio or 0.0,
        avg_commit_hour=m.avg_commit_hour or 12.0,
        burst_session_count=m.burst_session_count or 0,
        language_diversity=m.language_diversity or 0.0,
        pr_merge_ratio=m.pr_merge_ratio or 0.0,
        avg_files_per_commit=m.avg_files_per_commit or 0.0,
        code_churn_ratio=m.code_churn_ratio or 0.0,
        active_days_ratio=m.active_days_ratio or 0.0,
        computed_at=m.computed_at,
    )


@router.get("/personality", response_model=PersonalitySnapshotOut)
def latest_personality(user=Depends(get_current_user)):
    s = PersonalitySnapshot.objects(user=user).order_by("-created_at").first()
    if not s:
        raise HTTPException(status_code=404, detail="No personality snapshot found")
    return _snap_out(s)


@router.get("/history", response_model=List[PersonalitySnapshotOut])
def history(user=Depends(get_current_user)):
    return [_snap_out(s) for s in PersonalitySnapshot.objects(user=user).order_by("created_at")]


@router.get("/insights")
def insights(user=Depends(get_current_user)):
    """Return role prediction, work style, and trait reasoning for the latest snapshot."""
    s = PersonalitySnapshot.objects(user=user).order_by("-created_at").first()
    if not s:
        raise HTTPException(status_code=404, detail="Run an analysis first")
    return {
        "predicted_role":    s.predicted_role or "",
        "role_reason":       s.role_reason or "",
        "role_confidence":   s.role_confidence or 0.0,
        "work_style":        s.work_style or "",
        "work_style_detail": s.work_style_detail or "",
        "reasoning":         s.reasoning or {},
    }


def _snap_out(s: PersonalitySnapshot) -> PersonalitySnapshotOut:
    return PersonalitySnapshotOut(
        analytical=s.analytical, creativity=s.creativity,
        discipline=s.discipline, collaboration=s.collaboration,
        adaptability=s.adaptability, learning_velocity=s.learning_velocity,
        risk_appetite=s.risk_appetite, stress_stability=s.stress_stability,
        week=s.week or None,
        reasoning=s.reasoning or {},
        predicted_role=s.predicted_role or "",
        role_reason=s.role_reason or "",
        role_confidence=s.role_confidence or 0.0,
        work_style=s.work_style or "",
        work_style_detail=s.work_style_detail or "",
        created_at=s.created_at,
    )


# ── Language Breakdown ────────────────────────────────────────────────────────
@router.get("/languages")
def language_breakdown(user=Depends(get_current_user)):
    """Return language distribution from repos + per-language commit counts."""
    account = GitHubAccount.objects(user=user).first()
    if not account:
        raise HTTPException(status_code=404, detail="No GitHub account connected")
    repos = list(GitHubRepo.objects(account=account))
    if not repos:
        return {"languages": [], "total_repos": 0}

    lang_repos: Counter = Counter()
    lang_commits: Counter = Counter()
    lang_lines: Counter = Counter()

    for repo in repos:
        lang = repo.primary_language or "Unknown"
        lang_repos[lang] += 1
        commits = Commit.objects(repo=repo)
        for c in commits:
            lang_commits[lang] += 1
            lang_lines[lang] += c.additions + c.deletions

    total = sum(lang_repos.values())
    languages = []
    for lang, count in lang_repos.most_common(12):
        languages.append({
            "language": lang,
            "repos": count,
            "commits": lang_commits.get(lang, 0),
            "lines": lang_lines.get(lang, 0),
            "percent": round(count / total * 100, 1) if total else 0,
        })
    return {"languages": languages, "total_repos": total}


# ── Snapshot Comparison ───────────────────────────────────────────────────────
@router.get("/compare")
def compare_snapshots(user=Depends(get_current_user)):
    """Compare latest vs previous personality snapshot — trait deltas."""
    snaps = list(PersonalitySnapshot.objects(user=user).order_by("-created_at")[:2])
    if len(snaps) < 2:
        return {"available": False, "message": "Need at least 2 analysis runs to compare"}

    traits = ["analytical", "creativity", "discipline", "collaboration",
              "adaptability", "learning_velocity", "risk_appetite", "stress_stability"]
    latest, prev = snaps[0], snaps[1]
    deltas = {}
    for t in traits:
        new_val = getattr(latest, t, 0)
        old_val = getattr(prev, t, 0)
        deltas[t] = {"current": round(new_val, 1), "previous": round(old_val, 1),
                     "delta": round(new_val - old_val, 1)}

    return {
        "available": True,
        "latest_week": latest.week or "current",
        "previous_week": prev.week or "previous",
        "latest_role": latest.predicted_role or "",
        "previous_role": prev.predicted_role or "",
        "deltas": deltas,
    }


# ── Developer Summary ────────────────────────────────────────────────────────
@router.get("/summary")
def developer_summary(user=Depends(get_current_user)):
    """Generate a concise developer profile summary string."""
    snap = PersonalitySnapshot.objects(user=user).order_by("-created_at").first()
    metrics = FeatureMetrics.objects(user=user).order_by("-computed_at").first()
    account = GitHubAccount.objects(user=user).first()
    if not snap or not metrics:
        raise HTTPException(status_code=404, detail="Run an analysis first")

    traits = {
        "analytical": snap.analytical, "creativity": snap.creativity,
        "discipline": snap.discipline, "collaboration": snap.collaboration,
    }
    top_traits = sorted(traits.items(), key=lambda x: -x[1])[:2]
    top_names = [t[0].replace("_", " ").title() for t in top_traits]

    night = (metrics.night_commit_ratio or 0) * 100
    schedule = "night owl" if night > 40 else "early bird" if night < 15 else "balanced-hours"

    lines = [
        f"{account.github_login if account else user.email} is a {schedule} developer",
        f"with strong {top_names[0]} and {top_names[1]} tendencies.",
    ]
    if snap.predicted_role:
        lines.append(f"Best-fit role: {snap.predicted_role} ({snap.role_confidence:.0f}% confidence).")
    if snap.work_style:
        lines.append(f"Work style: {snap.work_style}.")
    lines.append(
        f"Across {metrics.total_repos or 0} repositories and {metrics.total_commits or 0} commits, "
        f"they demonstrate {snap.work_style_detail[:80] + '...' if len(snap.work_style_detail or '') > 80 else snap.work_style_detail or 'a consistent coding pattern'}."
    )

    # Activity heatmap data — commits per hour from events
    events = BehaviorEvent.objects(user=user, event_type="commit")
    hour_counts = [0] * 24
    day_counts = [0] * 7
    for e in events:
        if e.timestamp:
            hour_counts[e.timestamp.hour] += 1
            day_counts[e.timestamp.weekday()] += 1

    return {
        "bio": " ".join(lines),
        "github_login": account.github_login if account else "",
        "top_traits": top_names,
        "predicted_role": snap.predicted_role or "",
        "work_style": snap.work_style or "",
        "schedule_type": schedule,
        "hour_heatmap": hour_counts,   # 24 ints
        "day_heatmap": day_counts,     # 7 ints (Mon=0)
    }
