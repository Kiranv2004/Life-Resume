import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.github_ingestion.client import GitHubClient
from app.models.github import GitHubAccount
from app.schemas.github import GitHubConnectResponse, GitHubConnectedOut
from app.worker.tasks import run_analysis

router = APIRouter()


class PATConnectRequest(BaseModel):
    token: str


@router.get("/authorize", response_model=GitHubConnectResponse)
def authorize():
    if not settings.github_client_id:
        raise HTTPException(status_code=400, detail="GitHub OAuth is not configured")
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}&redirect_uri={settings.github_redirect_uri}&scope=repo"
    )
    return GitHubConnectResponse(authorization_url=url)


@router.post("/connect-pat")
def connect_pat(body: PATConnectRequest, user=Depends(get_current_user)):
    """Connect GitHub using a Personal Access Token."""
    client = GitHubClient(body.token)
    try:
        gh_user = client.get_user()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid GitHub token — check it has 'repo' scope")

    account = GitHubAccount.objects(user=user).first()
    if not account:
        account = GitHubAccount(user=user, github_login=gh_user["login"], access_token=body.token)
    else:
        account.github_login = gh_user["login"]
        account.access_token = body.token
    account.save()
    return {"connected": True, "github_login": gh_user["login"]}


@router.post("/callback")
def callback(code: str, user=Depends(get_current_user)):
    token = exchange_code_for_token(code)
    client = GitHubClient(token)
    gh_user = client.get_user()

    account = GitHubAccount.objects(user=user).first()
    if not account:
        account = GitHubAccount(user=user, github_login=gh_user["login"], access_token=token)
    else:
        account.github_login = gh_user["login"]
        account.access_token = token
    account.save()
    return {"connected": True, "github_login": gh_user["login"]}


@router.get("/status", response_model=GitHubConnectedOut)
def status(user=Depends(get_current_user)):
    account = GitHubAccount.objects(user=user).first()
    if not account:
        return GitHubConnectedOut(connected=False)
    return GitHubConnectedOut(connected=True, github_login=account.github_login)


@router.post("/start-analysis")
def start_analysis(user=Depends(get_current_user)):
    account = GitHubAccount.objects(user=user).first()
    if not account:
        raise HTTPException(status_code=400, detail="GitHub account not connected")
    from app.worker.tasks import run_analysis_background
    run_analysis_background(str(user.id))
    return {"status": "started"}


def exchange_code_for_token(code: str) -> str:
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
            "redirect_uri": settings.github_redirect_uri,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "access_token" not in data:
        raise HTTPException(status_code=400, detail="Failed to exchange GitHub code")
    return data["access_token"]
