"""
Authentication router - Registration, login, refresh token endpoints
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from freelance_app.models.base import get_db
from freelance_app.models.user import User
from freelance_app.schemas import UserRegister, UserLogin, Token, UserProfile
from freelance_app.utils.auth import AuthService, get_current_user, verify_refresh_token
from freelance_app.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, password, and full name"
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters with uppercase, digit, and special character
    - **full_name**: User's full name

    Returns the created user profile.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    password_hash = AuthService.get_password_hash(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        subscription_tier='free',
        is_active=True,
        email_verified=False,
        two_factor_enabled=False
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user and receive access and refresh tokens"
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password.

    - **email**: User's registered email
    - **password**: User's password

    Returns access token and refresh token for subsequent API calls.
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    try:
        db.commit()
    except Exception:
        db.rollback()
        # Don't fail login if timestamp update fails
        pass

    # Create access token
    access_token = AuthService.create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "subscription_tier": user.subscription_tier
        }
    )

    # Create refresh token
    refresh_token = AuthService.create_refresh_token(
        data={
            "user_id": user.id,
            "email": user.email
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Generate new access token using refresh token"
)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.

    - **refresh_token**: Valid refresh token received from login

    Returns a new access token.
    """
    # Verify refresh token and get user
    try:
        user = verify_refresh_token(refresh_token, db)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Check if user is still active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create new access token
    access_token = AuthService.create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "subscription_tier": user.subscription_tier
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user",
    description="Get the authenticated user's profile information"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.

    Requires authentication via Bearer token.

    Returns complete user profile including skills and preferences.
    """
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout current user (client should discard tokens)"
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout the current user.

    Note: JWT tokens are stateless, so the client must discard the tokens.
    This endpoint exists for consistency and potential future token blacklisting.

    Returns a success message.
    """
    return {
        "message": "Successfully logged out. Please discard your tokens.",
        "user_id": current_user.id
    }
