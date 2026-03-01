from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.github_ingestion.client import GitHubClient
from app.models.github import GitHubAccount, GitHubRepo, Commit, PullRequest, Issue, ReviewComment
from app.services.complexity import compute_commit_complexity


class GitHubIngestor:
    def __init__(self, db: Session, account: GitHubAccount):
        self.db = db
        self.account = account
        self.client = GitHubClient(account.access_token)

    def ingest(self) -> None:
        repos = self.client.list_repos()
        for repo in repos:
            repo_obj = self._upsert_repo(repo)
            self._ingest_commits(repo_obj)
            self._ingest_pull_requests(repo_obj)
            self._ingest_issues(repo_obj)
            self._ingest_review_comments(repo_obj)
        self.db.commit()

    def _upsert_repo(self, repo_data: dict) -> GitHubRepo:
        repo = (
            self.db.query(GitHubRepo)
            .filter(GitHubRepo.repo_id == repo_data["id"], GitHubRepo.account_id == self.account.id)
            .first()
        )
        if not repo:
            repo = GitHubRepo(account_id=self.account.id, repo_id=repo_data["id"])
            self.db.add(repo)
        repo.name = repo_data["name"]
        repo.full_name = repo_data["full_name"]
        repo.primary_language = repo_data.get("language")
        repo.created_at = self._parse_dt(repo_data.get("created_at"))
        repo.updated_at = self._parse_dt(repo_data.get("updated_at"))
        return repo

    def _ingest_commits(self, repo: GitHubRepo) -> None:
        commits = self.client.list_commits(repo.full_name)
        for item in commits:
            sha = item["sha"]
            existing = self.db.query(Commit).filter(Commit.sha == sha, Commit.repo_id == repo.id).first()
            if existing:
                continue
            detail = self.client.get_commit(repo.full_name, sha)
            stats = detail.get("stats", {})
            commit = Commit(
                repo_id=repo.id,
                sha=sha,
                author_date=self._parse_dt(detail["commit"]["author"]["date"]),
                additions=stats.get("additions", 0),
                deletions=stats.get("deletions", 0),
                total_changes=stats.get("total", 0),
                message=detail.get("commit", {}).get("message", ""),
                complexity_score=compute_commit_complexity(self.client, repo.full_name, sha, detail.get("files", [])),
            )
            self.db.add(commit)

    def _ingest_pull_requests(self, repo: GitHubRepo) -> None:
        pulls = self.client.list_pull_requests(repo.full_name)
        for pr in pulls:
            existing = self.db.query(PullRequest).filter(PullRequest.pr_id == pr["id"], PullRequest.repo_id == repo.id).first()
            if existing:
                continue
            item = PullRequest(
                repo_id=repo.id,
                pr_id=pr["id"],
                created_at=self._parse_dt(pr.get("created_at")),
                merged_at=self._parse_dt(pr.get("merged_at")),
            )
            self.db.add(item)

    def _ingest_issues(self, repo: GitHubRepo) -> None:
        issues = self.client.list_issues(repo.full_name)
        for issue in issues:
            if "pull_request" in issue:
                continue
            existing = self.db.query(Issue).filter(Issue.issue_id == issue["id"], Issue.repo_id == repo.id).first()
            if existing:
                continue
            item = Issue(
                repo_id=repo.id,
                issue_id=issue["id"],
                created_at=self._parse_dt(issue.get("created_at")),
                closed_at=self._parse_dt(issue.get("closed_at")),
                reopened=1 if issue.get("reopened_at") else 0,
            )
            self.db.add(item)

    def _ingest_review_comments(self, repo: GitHubRepo) -> None:
        comments = self.client.list_review_comments(repo.full_name)
        for comment in comments:
            existing = (
                self.db.query(ReviewComment)
                .filter(ReviewComment.comment_id == comment["id"], ReviewComment.repo_id == repo.id)
                .first()
            )
            if existing:
                continue
            item = ReviewComment(
                repo_id=repo.id,
                comment_id=comment["id"],
                created_at=self._parse_dt(comment.get("created_at")),
            )
            self.db.add(item)

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
