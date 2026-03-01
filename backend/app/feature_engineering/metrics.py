from __future__ import annotations
from statistics import mean, pstdev
from typing import List

from sqlalchemy.orm import Session

from app.models.github import Commit, Issue, ReviewComment, GitHubRepo, PullRequest


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
    reopened = len([i for i in issues if i.reopened])
    retry_commits = len([c for c in commits if "retry" in (c.message or "").lower()])
    return (reopened + retry_commits) / len(commits)


def complexity_handling_score(commits: List[Commit]) -> float:
    if not commits:
        return 0.0
    return mean(c.complexity_score for c in commits)


def compute_metrics(db: Session, user_id: int) -> dict:
    commits = db.query(Commit).join(GitHubRepo).join(GitHubRepo.account).filter(GitHubRepo.account.has(user_id=user_id)).all()
    repos = db.query(GitHubRepo).join(GitHubRepo.account).filter(GitHubRepo.account.has(user_id=user_id)).all()
    issues = db.query(Issue).join(GitHubRepo).join(GitHubRepo.account).filter(GitHubRepo.account.has(user_id=user_id)).all()
    review_comments = (
        db.query(ReviewComment).join(GitHubRepo).join(GitHubRepo.account).filter(GitHubRepo.account.has(user_id=user_id)).all()
    )
    pull_requests = (
        db.query(PullRequest).join(GitHubRepo).join(GitHubRepo.account).filter(GitHubRepo.account.has(user_id=user_id)).all()
    )

    return {
        "commit_consistency": commit_consistency_score(commits),
        "focus_depth": focus_depth_score(commits),
        "collaboration_index": collaboration_index(commits, review_comments, issues),
        "experimentation_index": experimentation_index(repos),
        "persistence_index": persistence_index(issues, commits),
        "complexity_handling": complexity_handling_score(commits),
        "pull_requests": len(pull_requests),
        "total_commits": len(commits),
    }
