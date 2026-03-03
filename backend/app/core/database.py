from mongoengine import connect, disconnect
from mongoengine.connection import ConnectionFailure, get_connection

from app.core.config import settings


def init_db() -> None:
    try:
        get_connection()
    except ConnectionFailure:
        connect(host=settings.mongodb_uri)


def close_db() -> None:
    disconnect()
