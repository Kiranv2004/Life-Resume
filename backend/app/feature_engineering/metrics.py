from __future__ import annotations
import math
from statistics import mean, pstdev
from typing import List

from bson import ObjectId

from app.models.analysis import BehaviorEvent
from app.models.github import Commit, Issue, ReviewComment, GitHubRepo, PullRequest, GitHubAccount
from app.models.user import User


# ─── Sigmoid helper: maps any positive value into 0–100 smoothly ─────────────
def _sigmoid100(x: float, midpoint: float, steepness: float = 1.0) -> float:
    """Logistic curve normalised to 0–100. midpoint = value that maps to 50."""
    try:
        return 100.0 / (1.0 + math.exp(-steepness * (x - midpoint)))
    except OverflowError:
        return 0.0 if x < midpoint else 100.0


def commit_consistency_score(commits: List[Commit]) -> float:
    if len(commits) < 2:
        return 0.0
    sorted_commits = sorted(commits, key=lambda c: c.author_date)
    intervals = [
        (sorted_commits[i].author_date - sorted_commits[i - 1].author_date).total_seconds()
        for i in range(1, len(sorted_commits))
    ]
    return pstdev(intervals)


def focus_depth_score(commits: List[Commit]) -> float:
    if not commits:
        return 0.0
    return mean(c.total_changes for c in commits)


def collaboration_index(commits: List[Commit], review_comments: List[ReviewComment], issues: List[Issue]) -> float:
    if not commits:
        return 0.0
    return (len(review_comments) + len(issues)) / len(commits)


def experimentation_index(repos: List[GitHubRepo]) -> float:
    if not repos:
        return 0.0
    new_repos = len([r for r in repos if r.created_at and r.updated_at and (r.updated_at - r.created_at).days < 90])
    return new_repos / len(repos)


def persistence_index(issues: List[Issue], commits: List[Commit]) -> float:
    if not commits:
        return 0.0
    reopened      = len([i for i in issues if i.reopened])
    retry_commits = len([c for c in commits if "retry" in (c.message or "").lower()
                         or "fix" in (c.message or "").lower()
                         or "bug" in (c.message or "").lower()])
    return (reopened + retry_commits) / len(commits)


def complexity_handling_score(commits: List[Commit]) -> float:
    if not commits:
        return 0.0
    return mean(c.complexity_score for c in commits)


# -- Extended behavioral signals ─────────────────────────────────────────────
def compute_night_ratio_and_hour(commit_events) -> tuple:
    if not commit_events:
        return 0.0, 12.0
    hours = [e.metadata.get("hour_of_day", 12) for e in commit_events]
    night = sum(1 for h in hours if h >= 20 or h <= 4)
    return round(night / len(hours), 3), round(mean(hours), 1)


def compute_burst_sessions(commit_events, window_seconds: int = 7200) -> int:
    if len(commit_events) < 3:
        return 0
    sorted_events = sorted(commit_events, key=lambda e: e.timestamp)
    bursts = 0
    i = 0
    while i < len(sorted_events) - 2:
        window_start = sorted_events[i].timestamp
        j = i + 1
        while j < len(sorted_events):
            delta = (sorted_events[j].timestamp - window_start).total_seconds()
            if delta <= window_seconds:
                j += 1
            else:
                break
        if j - i >= 3:
            bursts += 1
            i = j
        else:
            i += 1
    return bursts


# -- Additional enriched signals ─────────────────────────────────────────────
def _language_diversity(repos: List[GitHubRepo]) -> float:
    """Number of distinct primary languages across repos (0 → N)."""
    langs = {r.primary_language for r in repos if r.primary_language}
    return float(len(langs))


def _pr_merge_ratio(prs: List[PullRequest]) -> float:
    """Fraction of PRs that were merged (0–1)."""
    if not prs:
        return 0.0
    merged = sum(1 for p in prs if p.merged_at)
    return merged / len(prs)


def _avg_files_per_commit(commit_events) -> float:
    """Average number of files changed per commit from event metadata."""
    if not commit_events:
        return 0.0
    files_counts = [e.metadata.get("files_changed", 1) for e in commit_events]
    return mean(files_counts)


def _code_churn_ratio(commits: List[Commit]) -> float:
    """Ratio of deletions to total changes — how much code gets rewritten."""
    total = sum(c.total_changes for c in commits)
    if total == 0:
        return 0.0
    deletions = sum(c.deletions for c in commits)
    return deletions / total


def _active_days_ratio(commit_events, window_days: int = 30) -> float:
    """Fraction of unique days with commits in last N days."""
    if not commit_events:
        return 0.0
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    cutoff = now - timedelta(days=window_days)
    recent = [e for e in commit_events if e.timestamp and e.timestamp >= cutoff]
    if not recent:
        # Fall back to all events spread over their own range
        ts = sorted([e.timestamp for e in commit_events if e.timestamp])
        if len(ts) < 2:
            return 0.1
        span = max((ts[-1] - ts[0]).days, 1)
        unique_days = len({t.date() for t in ts})
        return min(1.0, unique_days / span)
    unique_days = len({e.timestamp.date() for e in recent})
    return min(1.0, unique_days / window_days)


def _empty_metrics() -> dict:
    return {
        "commit_consistency":    0.0,
        "focus_depth":           0.0,
        "collaboration_index":   0.0,
        "experimentation_index": 0.0,
        "persistence_index":     0.0,
        "complexity_handling":   0.0,
        "pull_requests":         0,
        "total_commits":         0,
        "total_repos":           0,
        "night_commit_ratio":    0.0,
        "avg_commit_hour":       12.0,
        "burst_session_count":   0,
        "language_diversity":    0.0,
        "pr_merge_ratio":        0.0,
        "avg_files_per_commit":  0.0,
        "code_churn_ratio":      0.0,
        "active_days_ratio":     0.0,
    }


def compute_metrics(user_id: str) -> dict:
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return _empty_metrics()
    account = GitHubAccount.objects(user=user).first()
    if not account:
        return _empty_metrics()

    repos           = list(GitHubRepo.objects(account=account))
    commits         = list(Commit.objects(repo__in=repos)) if repos else []
    issues          = list(Issue.objects(repo__in=repos)) if repos else []
    review_comments = list(ReviewComment.objects(repo__in=repos)) if repos else []
    pull_requests   = list(PullRequest.objects(repo__in=repos)) if repos else []

    commit_events   = list(BehaviorEvent.objects(user=user, event_type="commit").order_by("timestamp"))
    night_ratio, avg_hour = compute_night_ratio_and_hour(commit_events)
    burst_sessions        = compute_burst_sessions(commit_events)

    return {
        "commit_consistency":    commit_consistency_score(commits),
        "focus_depth":           focus_depth_score(commits),
        "collaboration_index":   collaboration_index(commits, review_comments, issues),
        "experimentation_index": experimentation_index(repos),
        "persistence_index":     persistence_index(issues, commits),
        "complexity_handling":   complexity_handling_score(commits),
        "pull_requests":         len(pull_requests),
        "total_commits":         len(commits),
        "total_repos":           len(repos),
        "night_commit_ratio":    night_ratio,
        "avg_commit_hour":       avg_hour,
        "burst_session_count":   burst_sessions,
        # New enriched signals
        "language_diversity":    _language_diversity(repos),
        "pr_merge_ratio":        _pr_merge_ratio(pull_requests),
        "avg_files_per_commit":  _avg_files_per_commit(commit_events),
        "code_churn_ratio":      _code_churn_ratio(commits),
        "active_days_ratio":     _active_days_ratio(commit_events),
    }