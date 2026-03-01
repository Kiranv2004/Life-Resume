import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.github_ingestion.client import GitHubClient
from app.models.github import GitHubAccount
from app.schemas.github import GitHubConnectResponse, GitHubConnectedOut
from app.worker.tasks import run_analysis

router = APIRouter()


@router.get("/authorize", response_model=GitHubConnectResponse)
def authorize():
    if not settings.github_client_id:
        raise HTTPException(status_code=400, detail="GitHub OAuth is not configured")
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}&redirect_uri={settings.github_redirect_uri}&scope=repo"
    )
    return GitHubConnectResponse(authorization_url=url)


@router.post("/callback")
def callback(code: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    token = exchange_code_for_token(code)
    client = GitHubClient(token)
    gh_user = client.get_user()

    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == user.id).first()
    if not account:
        account = GitHubAccount(user_id=user.id, github_login=gh_user["login"], access_token=token)
        db.add(account)
    else:
        account.github_login = gh_user["login"]
        account.access_token = token
    db.commit()
    return {"connected": True, "github_login": gh_user["login"]}


@router.get("/status", response_model=GitHubConnectedOut)
def status(db: Session = Depends(get_db), user=Depends(get_current_user)):
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == user.id).first()
    if not account:
        return GitHubConnectedOut(connected=False)
    return GitHubConnectedOut(connected=True, github_login=account.github_login)


@router.post("/start-analysis")
def start_analysis(db: Session = Depends(get_db), user=Depends(get_current_user)):
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=400, detail="GitHub account not connected")
    task = run_analysis.delay(user.id)
    return {"task_id": task.id}


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
