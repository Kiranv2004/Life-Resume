from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GitHubAccount(Base):
    __tablename__ = "github_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    github_login = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    connected_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="github_account")
    repos = relationship("GitHubRepo", back_populates="account")


class GitHubRepo(Base):
    __tablename__ = "github_repos"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("github_accounts.id"), nullable=False)
    repo_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    primary_language = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    account = relationship("GitHubAccount", back_populates="repos")
    commits = relationship("Commit", back_populates="repo")
    pull_requests = relationship("PullRequest", back_populates="repo")
    issues = relationship("Issue", back_populates="repo")


class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("github_repos.id"), nullable=False)
    sha = Column(String, nullable=False)
    author_date = Column(DateTime, nullable=False)
    additions = Column(Integer, nullable=False)
    deletions = Column(Integer, nullable=False)
    total_changes = Column(Integer, nullable=False)
    message = Column(String)
    complexity_score = Column(Float, default=0.0)

    repo = relationship("GitHubRepo", back_populates="commits")


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("github_repos.id"), nullable=False)
    pr_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    merged_at = Column(DateTime)

    repo = relationship("GitHubRepo", back_populates="pull_requests")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("github_repos.id"), nullable=False)
    issue_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime)
    reopened = Column(Integer, default=0)

    repo = relationship("GitHubRepo", back_populates="issues")


class ReviewComment(Base):
    __tablename__ = "review_comments"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("github_repos.id"), nullable=False)
    comment_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    repo = relationship("GitHubRepo")
