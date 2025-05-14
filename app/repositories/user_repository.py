from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from ..entities.database import Account, AccountType
from .base_repository import BaseRepository
import hashlib

class UserRepository(BaseRepository[Account]):
    def __init__(self, session: Session):
        super().__init__(session, Account)

    def create_account(self, username: str, email: str, password: str, account_type: AccountType) -> Account:
        """Create a new account with hashed password."""
        password_hash = self._hash_password(password)
        return self.create(
            username=username,
            email=email,
            password_hash=password_hash,
            account_type=account_type
        )

    def authenticate(self, username: str, password: str) -> Optional[Account]:
        """Authenticate an account by username and password."""
        password_hash = self._hash_password(password)
        stmt = select(Account).where(
            Account.username == username,
            Account.password_hash == password_hash,
            Account.account_type == AccountType.ADMINISTRATOR
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[Account]:
        """Get an account by username."""
        stmt = select(Account).where(Account.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[Account]:
        """Get an account by email."""
        stmt = select(Account).where(Account.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_type(self, account_type: AccountType) -> List[Account]:
        """Get all accounts with a specific type."""
        return self.filter_by(account_type=account_type)

    def update_password(self, account_id: int, new_password: str) -> Optional[Account]:
        """Update an account's password."""
        password_hash = self._hash_password(new_password)
        return self.update(account_id, password_hash=password_hash)

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest() 