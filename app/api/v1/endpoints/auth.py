from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.user import User
from pydantic import BaseModel, EmailStr

# Initialize logger for this module
logger = get_logger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserInfo(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: str
    school_id: str


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint - returns JWT token
    """
    logger.info(f"Login attempt for email: {login_data.email}")
    
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        logger.warning(f"Login failed - user not found: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning(
            f"Login failed - invalid password for user: {login_data.email}",
            extra={"extra_data": {"user_id": str(user.user_id)}}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.user_id)},
        expires_delta=access_token_expires
    )
    
    logger.info(
        f"Login successful for user: {login_data.email}",
        extra={
            "extra_data": {
                "user_id": str(user.user_id),
                "role": user.role.value,
                "school_id": str(user.school_id)
            }
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": str(user.user_id),
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role.value,
            "school_id": str(user.school_id)
        }
    }


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login (for Swagger UI)
    """
    logger.debug(f"Token login attempt for: {form_data.username}")
    
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Token login failed for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.user_id)},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Token login successful for: {form_data.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current user information from token
    """
    from app.api.dependencies import get_current_user
    
    logger.debug("Fetching current user info from token")
    
    user = await get_current_user(token, db)
    
    logger.debug(
        f"Retrieved user info for: {user.email}",
        extra={"extra_data": {"user_id": str(user.user_id)}}
    )
    
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role.value,
        "school_id": str(user.school_id)
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should delete token)
    """
    logger.info("User logout requested")
    return {"message": "Successfully logged out"}

