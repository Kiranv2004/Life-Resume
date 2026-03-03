from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    IntField,
    FloatField,
    ReferenceField,
)

from app.models.user import User


class GitHubAccount(Document):
    user = ReferenceField(User, required=True)
    github_login = StringField(required=True)
    access_token = StringField(required=True)
    connected_at = DateTimeField(default=datetime.utcnow)


class GitHubRepo(Document):
    account = ReferenceField(GitHubAccount, required=True)
    repo_id = IntField(required=True)
    name = StringField(required=True)
    full_name = StringField(required=True)
    primary_language = StringField()
    created_at = DateTimeField()
    updated_at = DateTimeField()


class Commit(Document):
    repo = ReferenceField(GitHubRepo, required=True)
    sha = StringField(required=True)
    author_date = DateTimeField(required=True)
    additions = IntField(required=True)
    deletions = IntField(required=True)
    total_changes = IntField(required=True)
    message = StringField()
    complexity_score = FloatField(default=0.0)


class PullRequest(Document):
    repo = ReferenceField(GitHubRepo, required=True)
    pr_id = IntField(required=True)
    created_at = DateTimeField(required=True)
    merged_at = DateTimeField()


class Issue(Document):
    repo = ReferenceField(GitHubRepo, required=True)
    issue_id = IntField(required=True)
    created_at = DateTimeField(required=True)
    closed_at = DateTimeField()
    reopened = IntField(default=0)


class ReviewComment(Document):
    repo = ReferenceField(GitHubRepo, required=True)
    comment_id = IntField(required=True)
    created_at = DateTimeField(required=True)
