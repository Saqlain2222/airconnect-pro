from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, sessionmaker
from .entities.database import User, engine
from .dto import TokenData
from .repositories.user_repository import UserRepository
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security configuration
JWT_SECRET = os.getenv("SECRET_KEY", "your-secret-key-here")  # Fallback for development
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRY_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

password_manager = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_scheme = OAuth2PasswordBearer(tokenUrl="token")

DatabaseSession = sessionmaker(bind=engine)

def validate_password(plain_text: str, hashed_text: str) -> bool:
    """Verify a password against its hash."""
    return password_manager.verify(plain_text, hashed_text)

def generate_password_hash(password: str) -> str:
    """Generate password hash."""
    return password_manager.hash(password)

def generate_jwt_token(data: dict, expiry: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    token_data = data.copy()
    if expiry:
        expiration = datetime.utcnow() + expiry
    else:
        expiration = datetime.utcnow() + timedelta(minutes=15)
    token_data.update({"exp": expiration})
    encoded_token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_token

async def get_authenticated_user(
    token: str = Depends(auth_scheme),
    session: Session = Depends(DatabaseSession)
) -> User:
    """Get current user from JWT token."""
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise auth_error
        token_info = TokenData(username=username)
    except JWTError:
        raise auth_error
    
    user_repo = UserRepository(session)
    user = user_repo.get_by_username(token_info.username)
    if user is None:
        raise auth_error
    return user

async def get_active_user(
    current_user: User = Depends(get_authenticated_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_database_session():
    """Dependency for getting database session."""
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close() 