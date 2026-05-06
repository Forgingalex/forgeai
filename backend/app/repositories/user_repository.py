"""User persistence repository."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for user lookups."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        """Return a user by username."""
        return self.db.query(User).filter(User.username == username).first()

