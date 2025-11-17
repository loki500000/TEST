"""
Pydantic schemas package for request/response validation
"""

# User schemas
from .user import (
    UserRegister,
    UserLogin,
    Token,
    UserProfile,
    UserProfileUpdate,
    UserSkillResponse,
    UserSkillCreate,
    UserPreferenceResponse,
    UserPreferenceUpdate,
)

# Job schemas
from .job import (
    JobResponse,
    JobSearchRequest,
    JobSearchResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)

# Client schemas
from .client import (
    ClientResponse,
    ClientVettingReport,
    ClientReviewResponse,
    ClientRedFlagResponse,
    ClientRedFlagCreate,
    ClientReviewCreate,
    CompanyResearchResponse,
    ScamReportCreate,
    ScamReportResponse,
    ClientSearchRequest,
    ClientSearchResponse,
)

__all__ = [
    # User schemas
    "UserRegister",
    "UserLogin",
    "Token",
    "UserProfile",
    "UserProfileUpdate",
    "UserSkillResponse",
    "UserSkillCreate",
    "UserPreferenceResponse",
    "UserPreferenceUpdate",
    # Job schemas
    "JobResponse",
    "JobSearchRequest",
    "JobSearchResponse",
    "JobApplicationCreate",
    "JobApplicationResponse",
    "JobApplicationUpdate",
    # Client schemas
    "ClientResponse",
    "ClientVettingReport",
    "ClientReviewResponse",
    "ClientRedFlagResponse",
    "ClientRedFlagCreate",
    "ClientReviewCreate",
    "CompanyResearchResponse",
    "ScamReportCreate",
    "ScamReportResponse",
    "ClientSearchRequest",
    "ClientSearchResponse",
]
