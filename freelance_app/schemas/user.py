"""
User-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserSkillResponse(BaseModel):
    """User skill response schema"""
    id: int = Field(..., description="Skill ID")
    skill_name: str = Field(..., description="Name of the skill")
    proficiency_level: Optional[str] = Field(None, description="Proficiency level (beginner, intermediate, expert)")
    years_experience: Optional[float] = Field(None, description="Years of experience")

    class Config:
        from_attributes = True


class UserPreferenceResponse(BaseModel):
    """User preference response schema"""
    id: int = Field(..., description="Preference ID")
    preferred_categories: Optional[List[str]] = Field(None, description="Preferred job categories")
    min_hourly_rate: Optional[float] = Field(None, description="Minimum hourly rate")
    max_hourly_rate: Optional[float] = Field(None, description="Maximum hourly rate")
    min_fixed_price: Optional[float] = Field(None, description="Minimum fixed price")
    preferred_job_types: Optional[List[str]] = Field(None, description="Preferred job types (hourly, fixed, both)")
    preferred_locations: Optional[List[str]] = Field(None, description="Preferred job locations")
    email_alerts_enabled: bool = Field(default=True, description="Email alerts enabled")
    alert_frequency: str = Field(default="daily", description="Alert frequency (realtime, hourly, daily, weekly)")

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile response schema"""
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="User's full name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    subscription_tier: str = Field(default="free", description="Subscription tier (free, pro, premium)")
    is_active: bool = Field(default=True, description="User active status")
    email_verified: bool = Field(default=False, description="Email verification status")
    two_factor_enabled: bool = Field(default=False, description="Two-factor authentication status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    skills: List[UserSkillResponse] = Field(default_factory=list, description="User skills")
    preferences: Optional[UserPreferenceResponse] = Field(None, description="User preferences")

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update schema"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's full name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    subscription_tier: Optional[str] = Field(None, description="Subscription tier (free, pro, premium)")

    @field_validator('subscription_tier')
    @classmethod
    def validate_subscription_tier(cls, v: Optional[str]) -> Optional[str]:
        """Validate subscription tier"""
        if v is not None and v not in ['free', 'pro', 'premium']:
            raise ValueError('Subscription tier must be one of: free, pro, premium')
        return v


class UserSkillCreate(BaseModel):
    """User skill creation schema"""
    skill_name: str = Field(..., min_length=1, max_length=100, description="Name of the skill")
    proficiency_level: str = Field(..., description="Proficiency level (beginner, intermediate, expert)")
    years_experience: Optional[float] = Field(None, ge=0, le=999.9, description="Years of experience")

    @field_validator('proficiency_level')
    @classmethod
    def validate_proficiency_level(cls, v: str) -> str:
        """Validate proficiency level"""
        if v not in ['beginner', 'intermediate', 'expert']:
            raise ValueError('Proficiency level must be one of: beginner, intermediate, expert')
        return v


class UserPreferenceUpdate(BaseModel):
    """User preference update schema"""
    preferred_categories: Optional[List[str]] = Field(None, description="Preferred job categories")
    min_hourly_rate: Optional[float] = Field(None, ge=0, description="Minimum hourly rate")
    max_hourly_rate: Optional[float] = Field(None, ge=0, description="Maximum hourly rate")
    min_fixed_price: Optional[float] = Field(None, ge=0, description="Minimum fixed price")
    preferred_job_types: Optional[List[str]] = Field(None, description="Preferred job types")
    preferred_locations: Optional[List[str]] = Field(None, description="Preferred job locations")
    email_alerts_enabled: Optional[bool] = Field(None, description="Email alerts enabled")
    alert_frequency: Optional[str] = Field(None, description="Alert frequency (realtime, hourly, daily, weekly)")

    @field_validator('alert_frequency')
    @classmethod
    def validate_alert_frequency(cls, v: Optional[str]) -> Optional[str]:
        """Validate alert frequency"""
        if v is not None and v not in ['realtime', 'hourly', 'daily', 'weekly']:
            raise ValueError('Alert frequency must be one of: realtime, hourly, daily, weekly')
        return v

    @model_validator(mode='after')
    def validate_hourly_rates(self):
        """Validate hourly rate constraints"""
        if self.min_hourly_rate and self.max_hourly_rate:
            if self.min_hourly_rate > self.max_hourly_rate:
                raise ValueError('min_hourly_rate cannot be greater than max_hourly_rate')
        return self
