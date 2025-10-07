from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from app.config import settings
import secrets

router = APIRouter(tags=["auth"])
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the admin password on startup
ADMIN_PASSWORD_HASH = pwd_context.hash(settings.admin_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Authenticate admin user"""
    # Check username
    is_correct_username = secrets.compare_digest(credentials.username, "admin")
    
    # Check password
    is_correct_password = verify_password(credentials.password, ADMIN_PASSWORD_HASH)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

@router.get("/verify")
async def verify_credentials(username: str = Depends(authenticate_admin)):
    """Verify admin credentials"""
    return {
        "authenticated": True,
        "username": username,
        "message": "Authentication successful"
    }