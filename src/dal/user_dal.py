from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from ..models.database import User, UserRole
from .base_dal import BaseDAL
import hashlib

class UserDAL(BaseDAL[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def create_user(self, username: str, email: str, password: str, role: UserRole) -> User:
        """Create a new user with hashed password."""
        password_hash = self._hash_password(password)
        return self.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        password_hash = self._hash_password(password)
        stmt = select(User).where(
            User.username == username,
            User.password_hash == password_hash,
            User.role == UserRole.ADMIN
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role."""
        return self.filter_by(role=role)

    def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Update a user's password."""
        password_hash = self._hash_password(new_password)
        return self.update(user_id, password_hash=password_hash)

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest() 