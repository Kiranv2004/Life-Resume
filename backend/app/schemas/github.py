from typing import Optional
from pydantic import BaseModel


class GitHubConnectResponse(BaseModel):
    authorization_url: str


class GitHubConnectedOut(BaseModel):
    connected: bool
    github_login: Optional[str] = None
