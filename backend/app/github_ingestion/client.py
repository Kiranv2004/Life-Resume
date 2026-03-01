from typing import Any, Dict, List
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str):
        self.token = token

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"token {self.token}", "Accept": "application/vnd.github+json"}

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _get(self, url: str, params: Dict[str, Any] | None = None) -> Any:
        response = requests.get(url, headers=self._headers(), params=params, timeout=30)
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(response.headers.get("X-RateLimit-Reset", "0"))
            raise RuntimeError(f"Rate limit exceeded. Reset at {reset}.")
        response.raise_for_status()
        return response.json()

    def get_user(self) -> Dict[str, Any]:
        return self._get(f"{GITHUB_API}/user")

    def list_repos(self) -> List[Dict[str, Any]]:
        return self._get(f"{GITHUB_API}/user/repos", params={"per_page": 100, "sort": "updated"})

    def list_commits(self, full_name: str) -> List[Dict[str, Any]]:
        return self._get(f"{GITHUB_API}/repos/{full_name}/commits", params={"per_page": 100})

    def get_commit(self, full_name: str, sha: str) -> Dict[str, Any]:
        return self._get(f"{GITHUB_API}/repos/{full_name}/commits/{sha}")

    def list_pull_requests(self, full_name: str) -> List[Dict[str, Any]]:
        return self._get(f"{GITHUB_API}/repos/{full_name}/pulls", params={"state": "all", "per_page": 100})

    def list_issues(self, full_name: str) -> List[Dict[str, Any]]:
        return self._get(f"{GITHUB_API}/repos/{full_name}/issues", params={"state": "all", "per_page": 100})

    def list_review_comments(self, full_name: str) -> List[Dict[str, Any]]:
        return self._get(f"{GITHUB_API}/repos/{full_name}/pulls/comments", params={"per_page": 100})

    def get_file_content(self, full_name: str, path: str, ref: str) -> str:
        data = self._get(f"{GITHUB_API}/repos/{full_name}/contents/{path}", params={"ref": ref})
        if isinstance(data, dict) and data.get("encoding") == "base64":
            import base64

            return base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        return ""
