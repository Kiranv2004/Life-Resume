from datetime import datetime
from mongoengine import Document, StringField, DateTimeField


class User(Document):
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
