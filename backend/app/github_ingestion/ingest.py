from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Callable, List, Optional, Tuple

from app.github_ingestion.client import GitHubClient
from app.models.analysis import BehaviorEvent
from app.models.github import GitHubAccount, GitHubRepo, Commit, PullRequest, Issue, ReviewComment
from app.models.user import User
from app.services.complexity import compute_commit_complexity

_noop = lambda msg: None  # noqa: E731

# Workers for parallel API calls — aggressive for speed
_COMMIT_WORKERS = 12   # parallel get_commit fetches per repo
_REPO_WORKERS   = 6    # parallel repo processing
_SUB_WORKERS    = 4    # parallel PR / issue / review fetches inside each repo


class GitHubIngestor:
    def __init__(self, account: GitHubAccount, max_repos: int = 10, max_commits: int = 15):
        self.account     = account
        self.client      = GitHubClient(account.access_token)
        self.user: User  = account.user
        self.max_repos   = max_repos
        self.max_commits = max_commits

    # -- Public entry point -----------------------------------------------
    def ingest(self, log_fn: Callable[[str], None] = _noop) -> Tuple[int, int]:
        all_repos = self.client.list_repos()
        repos_to_process = all_repos[: self.max_repos]
        log_fn(f"Found {len(all_repos)} repos -- processing top {len(repos_to_process)}")

        total_commits = 0
        results: List[int] = []

        with ThreadPoolExecutor(max_workers=_REPO_WORKERS) as pool:
            futures = {
                pool.submit(self._process_repo, repo, log_fn): repo
                for repo in repos_to_process
            }
            for fut in as_completed(futures):
                try:
                    c = fut.result()
                    results.append(c)
                except Exception as e:
                    repo = futures[fut]
                    log_fn(f"  [{repo['name']}] failed: {e.__class__.__name__}: {e}")

        total_commits = sum(results)
        return len(repos_to_process), total_commits

    def _process_repo(self, repo_data: dict, log_fn: Callable) -> int:
        repo_name = repo_data["name"]
        log_fn(f"  Processing {repo_name}")
        repo_obj = self._upsert_repo(repo_data)

        # Fetch commits, PRs, issues, and reviews ALL in parallel
        with ThreadPoolExecutor(max_workers=_SUB_WORKERS) as pool:
            f_commits = pool.submit(self._ingest_commits, repo_obj, repo_name, log_fn)
            f_prs     = pool.submit(self._ingest_pull_requests, repo_obj, repo_name)
            f_issues  = pool.submit(self._ingest_issues, repo_obj, repo_name)
            f_reviews = pool.submit(self._ingest_review_comments, repo_obj, repo_name)

            # Wait for all — commits return count, others return None
            count = f_commits.result()
            f_prs.result()
            f_issues.result()
            f_reviews.result()

        return count

    def _upsert_repo(self, repo_data: dict) -> GitHubRepo:
        repo = GitHubRepo.objects(account=self.account, repo_id=repo_data["id"]).first()
        if not repo:
            repo = GitHubRepo(account=self.account, repo_id=repo_data["id"])
        repo.name             = repo_data["name"]
        repo.full_name        = repo_data["full_name"]
        repo.primary_language = repo_data.get("language")
        repo.created_at       = self._parse_dt(repo_data.get("created_at"))
        repo.updated_at       = self._parse_dt(repo_data.get("updated_at"))
        repo.save()
        return repo

    def _ingest_commits(self, repo: GitHubRepo, repo_name: str, log_fn: Callable) -> int:
        try:
            raw_commits = self.client.list_commits(repo.full_name, per_page=self.max_commits)
        except Exception as e:
            log_fn(f"    [{repo_name}] Skipping commits ({e.__class__.__name__})")
            return 0

        to_process = raw_commits[: self.max_commits]
        if not to_process:
            return 0

        new_shas = [
            item["sha"] for item in to_process
            if not Commit.objects(repo=repo, sha=item["sha"]).first()
        ]

        if not new_shas:
            log_fn(f"    [{repo_name}] all {len(to_process)} commits already stored")
            return len(to_process)

        details = {}
        with ThreadPoolExecutor(max_workers=_COMMIT_WORKERS) as pool:
            future_map = {
                pool.submit(self.client.get_commit, repo.full_name, sha): sha
                for sha in new_shas
            }
            for fut in as_completed(future_map):
                sha = future_map[fut]
                try:
                    details[sha] = fut.result()
                except Exception:
                    pass

        saved = 0
        for sha, detail in details.items():
            try:
                stats      = detail.get("stats", {})
                files      = detail.get("files", [])
                author_dt  = self._parse_dt(detail["commit"]["author"]["date"])
                complexity = compute_commit_complexity(None, repo.full_name, sha, files)

                Commit(
                    repo=repo, sha=sha,
                    author_date=author_dt,
                    additions=stats.get("additions", 0),
                    deletions=stats.get("deletions", 0),
                    total_changes=stats.get("total", 0),
                    message=detail.get("commit", {}).get("message", ""),
                    complexity_score=complexity,
                ).save()

                if author_dt:
                    BehaviorEvent(
                        user=self.user,
                        event_type="commit",
                        timestamp=author_dt,
                        metadata={
                            "repo":          repo_name,
                            "additions":     stats.get("additions", 0),
                            "deletions":     stats.get("deletions", 0),
                            "files_changed": len(files),
                            "complexity":    complexity,
                            "hour_of_day":   author_dt.hour,
                        },
                    ).save()
                saved += 1
            except Exception:
                continue

        log_fn(f"    [{repo_name}] {saved} new / {len(to_process)} total commits")
        return len(to_process)

    def _ingest_pull_requests(self, repo: GitHubRepo, repo_name: str) -> None:
        for pr in self.client.list_pull_requests(repo.full_name):
            if PullRequest.objects(repo=repo, pr_id=pr["id"]).first():
                continue
            created = self._parse_dt(pr.get("created_at"))
            merged  = self._parse_dt(pr.get("merged_at"))
            PullRequest(repo=repo, pr_id=pr["id"], created_at=created, merged_at=merged).save()
            if created:
                BehaviorEvent(
                    user=self.user,
                    event_type="pull_request",
                    timestamp=created,
                    metadata={"repo": repo_name, "merged": merged is not None},
                ).save()

    def _ingest_issues(self, repo: GitHubRepo, repo_name: str) -> None:
        for issue in self.client.list_issues(repo.full_name):
            if "pull_request" in issue:
                continue
            if Issue.objects(repo=repo, issue_id=issue["id"]).first():
                continue
            created = self._parse_dt(issue.get("created_at"))
            Issue(
                repo=repo, issue_id=issue["id"],
                created_at=created,
                closed_at=self._parse_dt(issue.get("closed_at")),
                reopened=1 if issue.get("reopened_at") else 0,
            ).save()
            if created:
                BehaviorEvent(
                    user=self.user,
                    event_type="issue",
                    timestamp=created,
                    metadata={"repo": repo_name},
                ).save()

    def _ingest_review_comments(self, repo: GitHubRepo, repo_name: str) -> None:
        for comment in self.client.list_review_comments(repo.full_name):
            if ReviewComment.objects(repo=repo, comment_id=comment["id"]).first():
                continue
            created = self._parse_dt(comment.get("created_at"))
            ReviewComment(repo=repo, comment_id=comment["id"], created_at=created).save()
            if created:
                BehaviorEvent(
                    user=self.user,
                    event_type="review_comment",
                    timestamp=created,
                    metadata={"repo": repo_name},
                ).save()

    @staticmethod
    def _parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)