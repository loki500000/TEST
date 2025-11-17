"""
Job-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class JobResponse(BaseModel):
    """Job response schema"""
    id: int = Field(..., description="Job ID")
    external_job_id: Optional[str] = Field(None, description="External job ID from platform")
    title: str = Field(..., description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    category: Optional[str] = Field(None, description="Job category")
    subcategory: Optional[str] = Field(None, description="Job subcategory")
    skills_required: Optional[List[str]] = Field(None, description="Required skills")
    job_type: str = Field(..., description="Job type (hourly, fixed, both)")
    budget_min: Optional[Decimal] = Field(None, ge=0, description="Minimum budget")
    budget_max: Optional[Decimal] = Field(None, ge=0, description="Maximum budget")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="Hourly rate")
    fixed_price: Optional[Decimal] = Field(None, ge=0, description="Fixed price")
    duration: Optional[str] = Field(None, description="Project duration")
    experience_level: Optional[str] = Field(None, description="Required experience level (entry, intermediate, expert)")
    applications_count: int = Field(default=0, description="Number of applications")
    is_active: bool = Field(default=True, description="Job active status")
    posted_date: Optional[datetime] = Field(None, description="Job posted date")
    job_url: Optional[str] = Field(None, description="Job URL on platform")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    client_id: Optional[int] = Field(None, description="Client ID")

    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    """Job search request schema"""
    search_query: Optional[str] = Field(None, max_length=500, description="Search query")
    category: Optional[str] = Field(None, description="Job category filter")
    job_type: Optional[str] = Field(None, description="Job type filter (hourly, fixed, both)")
    experience_level: Optional[str] = Field(None, description="Experience level filter")
    min_budget: Optional[Decimal] = Field(None, ge=0, description="Minimum budget")
    max_budget: Optional[Decimal] = Field(None, ge=0, description="Maximum budget")
    min_hourly_rate: Optional[Decimal] = Field(None, ge=0, description="Minimum hourly rate")
    max_hourly_rate: Optional[Decimal] = Field(None, ge=0, description="Maximum hourly rate")
    skills: Optional[List[str]] = Field(None, description="Required skills filter")
    is_active: bool = Field(default=True, description="Only active jobs")
    sort_by: Optional[str] = Field(default="posted_date", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc, desc)")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Results per page")

    @field_validator('job_type')
    @classmethod
    def validate_job_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate job type"""
        if v is not None and v not in ['hourly', 'fixed', 'both']:
            raise ValueError('Job type must be one of: hourly, fixed, both')
        return v

    @field_validator('experience_level')
    @classmethod
    def validate_experience_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate experience level"""
        if v is not None and v not in ['entry', 'intermediate', 'expert']:
            raise ValueError('Experience level must be one of: entry, intermediate, expert')
        return v

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        """Validate sort order"""
        if v is not None and v not in ['asc', 'desc']:
            raise ValueError('Sort order must be one of: asc, desc')
        return v

    @model_validator(mode='after')
    def validate_budget_range(self):
        """Validate budget range constraints"""
        if self.min_budget and self.max_budget:
            if self.min_budget > self.max_budget:
                raise ValueError('min_budget cannot be greater than max_budget')
        if self.min_hourly_rate and self.max_hourly_rate:
            if self.min_hourly_rate > self.max_hourly_rate:
                raise ValueError('min_hourly_rate cannot be greater than max_hourly_rate')
        return self


class JobSearchResponse(BaseModel):
    """Job search response schema"""
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Results per page")
    total_pages: int = Field(..., description="Total number of pages")
    jobs: List[JobResponse] = Field(..., description="List of jobs")

    class Config:
        from_attributes = True


class JobApplicationCreate(BaseModel):
    """Job application creation schema"""
    job_id: int = Field(..., description="Job ID")
    proposal_text: str = Field(..., min_length=10, max_length=5000, description="Application proposal text")
    bid_amount: Optional[Decimal] = Field(None, ge=0, description="Bid amount")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")


class JobApplicationResponse(BaseModel):
    """Job application response schema"""
    id: int = Field(..., description="Application ID")
    user_id: int = Field(..., description="User ID")
    job_id: int = Field(..., description="Job ID")
    applied_at: datetime = Field(..., description="Application timestamp")
    status: str = Field(default="applied", description="Application status (applied, shortlisted, rejected, hired)")
    proposal_text: str = Field(..., description="Proposal text")
    bid_amount: Optional[Decimal] = Field(None, description="Bid amount")
    notes: Optional[str] = Field(None, description="Additional notes")
    job: Optional[JobResponse] = Field(None, description="Associated job details")

    class Config:
        from_attributes = True


class JobApplicationUpdate(BaseModel):
    """Job application update schema"""
    status: Optional[str] = Field(None, description="New status")
    proposal_text: Optional[str] = Field(None, min_length=10, max_length=5000, description="Updated proposal text")
    bid_amount: Optional[Decimal] = Field(None, ge=0, description="Updated bid amount")
    notes: Optional[str] = Field(None, max_length=2000, description="Updated notes")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate application status"""
        if v is not None and v not in ['applied', 'shortlisted', 'rejected', 'hired']:
            raise ValueError('Status must be one of: applied, shortlisted, rejected, hired')
        return v
