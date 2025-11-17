"""
Client-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class ClientResponse(BaseModel):
    """Client response schema"""
    id: int = Field(..., description="Client ID")
    external_client_id: Optional[str] = Field(None, description="External client ID from platform")
    name: Optional[str] = Field(None, description="Client name")
    company_name: Optional[str] = Field(None, description="Company name")
    profile_url: Optional[str] = Field(None, description="Profile URL")
    location: Optional[str] = Field(None, description="Client location")
    timezone: Optional[str] = Field(None, description="Client timezone")
    member_since: Optional[date] = Field(None, description="Member since date")
    total_jobs_posted: int = Field(default=0, description="Total jobs posted")
    total_hires: int = Field(default=0, description="Total hires")
    total_spent: Decimal = Field(default=Decimal('0'), description="Total amount spent")
    payment_verified: bool = Field(default=False, description="Payment verification status")
    average_rating: Optional[Decimal] = Field(None, ge=0, le=5, description="Average rating (0-5)")
    response_time_hours: Optional[int] = Field(None, ge=0, description="Response time in hours")
    project_completion_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Project completion rate (0-100)")
    trust_score: Optional[int] = Field(None, ge=0, le=100, description="Trust score (0-100)")
    last_active: Optional[datetime] = Field(None, description="Last active timestamp")
    is_verified: bool = Field(default=False, description="Verification status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ClientReviewResponse(BaseModel):
    """Client review response schema"""
    id: int = Field(..., description="Review ID")
    client_id: int = Field(..., description="Client ID")
    reviewer_name: Optional[str] = Field(None, description="Reviewer name")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    review_text: Optional[str] = Field(None, description="Review text")
    project_title: Optional[str] = Field(None, description="Project title")
    project_value: Optional[Decimal] = Field(None, ge=0, description="Project value")
    review_date: Optional[date] = Field(None, description="Review date")
    sentiment_score: Optional[Decimal] = Field(None, ge=-1, le=1, description="Sentiment score (-1 to 1)")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class ClientRedFlagResponse(BaseModel):
    """Client red flag response schema"""
    id: int = Field(..., description="Red flag ID")
    client_id: int = Field(..., description="Client ID")
    flag_type: str = Field(..., description="Type of red flag")
    description: Optional[str] = Field(None, description="Flag description")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    detected_at: datetime = Field(..., description="Detection timestamp")
    is_resolved: bool = Field(default=False, description="Resolution status")

    class Config:
        from_attributes = True


class CompanyResearchResponse(BaseModel):
    """Company research response schema"""
    id: int = Field(..., description="Research ID")
    client_id: int = Field(..., description="Client ID")
    company_name: Optional[str] = Field(None, description="Company name")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn URL")
    linkedin_found: bool = Field(default=False, description="LinkedIn profile found")
    linkedin_employee_count: Optional[int] = Field(None, ge=0, description="LinkedIn employee count")
    website_url: Optional[str] = Field(None, description="Company website URL")
    website_found: bool = Field(default=False, description="Website found")
    social_media_presence: Optional[Dict[str, Any]] = Field(None, description="Social media presence data")
    recent_news: Optional[Dict[str, Any]] = Field(None, description="Recent news data")
    digital_footprint_score: Optional[int] = Field(None, ge=0, le=100, description="Digital footprint score (0-100)")
    research_date: datetime = Field(..., description="Research date")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class ScamReportCreate(BaseModel):
    """Scam report creation schema"""
    client_id: Optional[int] = Field(None, description="Client ID (if reporting client)")
    job_id: Optional[int] = Field(None, description="Job ID (if reporting job)")
    report_type: str = Field(..., min_length=1, max_length=100, description="Type of scam/issue")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed description of the issue")
    evidence_urls: Optional[List[str]] = Field(None, description="URLs to evidence")

    @model_validator(mode='after')
    def validate_at_least_one_target(self):
        """Validate that either client_id or job_id is provided"""
        if not self.client_id and not self.job_id:
            raise ValueError('Either client_id or job_id must be provided')
        return self


class ScamReportResponse(BaseModel):
    """Scam report response schema"""
    id: int = Field(..., description="Report ID")
    client_id: Optional[int] = Field(None, description="Client ID")
    reporter_user_id: Optional[int] = Field(None, description="Reporter user ID")
    job_id: Optional[int] = Field(None, description="Job ID")
    report_type: str = Field(..., description="Report type")
    description: str = Field(..., description="Report description")
    evidence_urls: Optional[List[str]] = Field(None, description="Evidence URLs")
    status: str = Field(default="pending", description="Report status (pending, confirmed, dismissed)")
    upvotes: int = Field(default=0, ge=0, description="Number of upvotes")
    downvotes: int = Field(default=0, ge=0, description="Number of downvotes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ClientVettingReport(BaseModel):
    """Comprehensive client vetting report schema"""
    client: ClientResponse = Field(..., description="Client information")
    reviews: List[ClientReviewResponse] = Field(default_factory=list, description="Client reviews")
    red_flags: List[ClientRedFlagResponse] = Field(default_factory=list, description="Red flags detected")
    company_research: Optional[CompanyResearchResponse] = Field(None, description="Company research data")
    scam_reports: List[ScamReportResponse] = Field(default_factory=list, description="Scam reports")
    overall_risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    recommendation: str = Field(..., description="Vetting recommendation")
    summary: str = Field(..., description="Summary of findings")
    report_generated_at: datetime = Field(..., description="Report generation timestamp")

    class Config:
        from_attributes = True


class ClientRedFlagCreate(BaseModel):
    """Client red flag creation schema"""
    flag_type: str = Field(..., min_length=1, max_length=100, description="Type of red flag")
    description: Optional[str] = Field(None, max_length=2000, description="Flag description")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity level"""
        if v not in ['low', 'medium', 'high', 'critical']:
            raise ValueError('Severity must be one of: low, medium, high, critical')
        return v


class ClientReviewCreate(BaseModel):
    """Client review creation schema"""
    reviewer_name: Optional[str] = Field(None, max_length=255, description="Reviewer name")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    review_text: str = Field(..., min_length=10, max_length=5000, description="Review text")
    project_title: Optional[str] = Field(None, max_length=255, description="Project title")
    project_value: Optional[Decimal] = Field(None, ge=0, description="Project value")
    review_date: Optional[date] = Field(None, description="Review date")


class ClientSearchRequest(BaseModel):
    """Client search request schema"""
    search_query: Optional[str] = Field(None, max_length=500, description="Search query")
    min_trust_score: Optional[int] = Field(None, ge=0, le=100, description="Minimum trust score")
    max_trust_score: Optional[int] = Field(None, ge=0, le=100, description="Maximum trust score")
    payment_verified_only: bool = Field(default=False, description="Only show payment verified clients")
    is_verified_only: bool = Field(default=False, description="Only show verified clients")
    min_rating: Optional[Decimal] = Field(None, ge=0, le=5, description="Minimum average rating")
    sort_by: Optional[str] = Field(default="trust_score", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc, desc)")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Results per page")

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        """Validate sort order"""
        if v is not None and v not in ['asc', 'desc']:
            raise ValueError('Sort order must be one of: asc, desc')
        return v

    @model_validator(mode='after')
    def validate_trust_score_range(self):
        """Validate trust score range"""
        if self.min_trust_score and self.max_trust_score:
            if self.min_trust_score > self.max_trust_score:
                raise ValueError('min_trust_score cannot be greater than max_trust_score')
        return self


class ClientSearchResponse(BaseModel):
    """Client search response schema"""
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Results per page")
    total_pages: int = Field(..., description="Total number of pages")
    clients: List[ClientResponse] = Field(..., description="List of clients")

    class Config:
        from_attributes = True
