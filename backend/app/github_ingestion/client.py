from typing import Any, Dict, List, Optional
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str):
        self.token = token

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"token {self.token}", "Accept": "application/vnd.github+json"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=4),
        reraise=True,
        retry=retry_if_exception_type(requests.exceptions.ConnectionError),
    )
    def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        response = requests.get(url, headers=self._headers(), params=params, timeout=12)
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "1")
            if remaining == "0":
                reset = int(response.headers.get("X-RateLimit-Reset", "0"))
                raise RuntimeError(f"GitHub rate limit exceeded. Reset at {reset}.")
            # Other 403 (private repo, forbidden) — don't retry
            raise requests.exceptions.HTTPError(response=response)
        if response.status_code in (404, 451):
            # Not found / unavailable — don't retry
            raise requests.exceptions.HTTPError(response=response)
        if response.status_code >= 500:
            response.raise_for_status()  # will be retried by tenacity
        response.raise_for_status()
        return response.json()

    def get_user(self) -> Dict[str, Any]:
        return self._get(f"{GITHUB_API}/user")

    def list_repos(self) -> List[Dict[str, Any]]:
        return self._get(f"{GITHUB_API}/user/repos", params={"per_page": 100, "sort": "updated"})

    def list_commits(self, full_name: str, per_page: int = 15) -> List[Dict[str, Any]]:
        try:
            return self._get(f"{GITHUB_API}/repos/{full_name}/commits", params={"per_page": per_page})
        except Exception:
            return []

    def get_commit(self, full_name: str, sha: str) -> Dict[str, Any]:
        return self._get(f"{GITHUB_API}/repos/{full_name}/commits/{sha}")

    def list_pull_requests(self, full_name: str) -> List[Dict[str, Any]]:
        try:
            return self._get(f"{GITHUB_API}/repos/{full_name}/pulls", params={"state": "all", "per_page": 100})
        except Exception:
            return []

    def list_issues(self, full_name: str) -> List[Dict[str, Any]]:
        try:
            return self._get(f"{GITHUB_API}/repos/{full_name}/issues", params={"state": "all", "per_page": 100})
        except Exception:
            return []

    def list_review_comments(self, full_name: str) -> List[Dict[str, Any]]:
        try:
            return self._get(f"{GITHUB_API}/repos/{full_name}/pulls/comments", params={"per_page": 100})
        except Exception:
            return []

    def get_file_content(self, full_name: str, path: str, ref: str) -> str:
        data = self._get(f"{GITHUB_API}/repos/{full_name}/contents/{path}", params={"ref": ref})
        if isinstance(data, dict) and data.get("encoding") == "base64":
            import base64

            return base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        return ""
